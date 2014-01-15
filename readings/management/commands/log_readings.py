import datetime
import time
from multiprocessing.dummy import Pool
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import simplejson as json

from boto.exception import SQSError

from readings.serializers import ReadingListSerializer

from utils.dynamodb import get_conn, write_items
from utils.loggly import Logger
from utils.queue import get_queue
from utils.s3 import get_bucket, read_from_bucket, write_to_bucket
from utils.statistics import mean, median, std_dev
from utils import geohash


# Utility functions
def hash_dict(data):
    return '%s%s%s' % (
        data['latitude'],
        data['longitude'],
        data['daterecorded'],
    )


def group_by(items, length):
    while items:
        yield items[:length]
        items = items[length:]


# Handlers
class DataHandler(Logger):

    def __init__(self, bucket=None, input_path=None):
        self.bucket = bucket
        self.input_path = input_path

    def merge_data(self, existing_data, new_data):
        existing_dict = dict([(hash_dict(record), record) for record in existing_data])
        new_dict = dict([(hash_dict(record), record) for record in new_data])

        existing_dict.update(new_dict)

        return existing_dict.values()

    def get_existing_data(self, duration_label, key):
        input_file = '%s%s/%s.json' % (self.input_path, duration_label, key)

        existing_content = read_from_bucket(self.bucket, input_file)
        if existing_content:
            return json.loads(existing_content)

    def process_data(self, data):
        return data

    def write_data(self, data):
        return 'no output'

    def handle(self, duration_label, key, data):
        try:
            start = time.time()

            existing_data = self.get_existing_data(duration_label, key)
            if existing_data:
                data = self.merge_data(existing_data, data)

            processed_data = self.process_data(data)

            output = self.write_data(duration_label, key, processed_data)

            end = time.time()

            self.log(
                output=output,
                duration=duration_label,
                time=(end - start),
                count=len(processed_data),
                bucket=str(self.bucket),
            )
        except Exception, e:
            self.log(
                error=str(e)
            )


class S3Handler(DataHandler):

    def __init__(self, output_path=None, **kwargs):
        self.output_path = output_path
        super(S3Handler, self).__init__(**kwargs)

    def process_data(self, data):
        return data

    def write_data(self, duration_label, key, data):
        output_file = '%s%s/%s.json' % (self.output_path, duration_label, key)

        output_content = json.dumps(data)

        write_to_bucket(
            self.bucket,
            output_file,
            output_content,
            'application/json',
            compress=True,
        )

        return output_file

    def log(self, **kwargs):
        super(S3Handler, self).log(
            event='write to s3',
            **kwargs
        )


class S3FilteredHandler(S3Handler):

    def __init__(self, allowed_fields=None, **kwargs):
        self.allowed_fields = allowed_fields
        super(S3FilteredHandler, self).__init__(**kwargs)

    def process_data(self, data):
        if self.allowed_fields:
            filtered_data = []

            for data_point in data:
                filtered_data_point = dict([
                    (field, value) for (field, value) in data_point.items()
                        if field in self.allowed_fields
                ])

                filtered_data.append(filtered_data_point)

        else:
            filtered_data = data

        return filtered_data


class DynamoDBHandler(DataHandler):

    def __init__(self, conn=None, table=None, **kwargs):
        self.conn = conn
        self.table = table
        super(DynamoDBHandler, self).__init__(**kwargs)

    def process_data(self, data):
        geo_sorted = defaultdict(list)

        for data_point in data:
            for geo_key_length in range(1, 6):
                geo_key = geohash.encode(
                    data_point['latitude'],
                    data_point['longitude'],
                    precision=geo_key_length,
                )
                geo_sorted[geo_key].append(data_point)

        statistics = {}

        for geo_key, data_points in geo_sorted.items():
            readings = [data_point['reading'] for data_point in data_points]
            unique_users = len(set([data_point['user_id'] for data_point in data_points]))

            statistics[geo_key] = {
                'min': min(readings),
                'max': max(readings),
                'mean': mean(readings),
                'median': median(readings),
                'std_dev': std_dev(readings),
                'samples': len(readings),
                'users': unique_users,
            }

        return statistics

    def write_data(self, duration_label, key, data):
        put_items = [
            self.table.new_item(
                hash_key='%s-%s' % (duration_label, geo_key),
                range_key=key,
                attrs=stats,
            ) for geo_key, stats in data.items()]

        for batch_items in group_by(put_items, 25):
            write_items(self.conn, self.table, batch_items)

        return '%s: %s' % (duration_label, key)

    def log(self, **kwargs):
        super(DynamoDBHandler, self).log(
            event='write to dynamodb',
            table=str(self.table),
            **kwargs
        )


class QueueAggregator(Logger):

    def __init__(self, queue=None, handlers=None, persist_duration=None, log_durations=None):
        self.queue = queue
        self.handlers = handlers
        self.persist_duration = persist_duration
        self.log_durations = log_durations

        self.active_messages = {}
        self.persisted_messages = set()
        self.blocks = defaultdict(lambda: defaultdict(dict))
        self.last_handled_date = datetime.datetime.now()

        self.log(
            event='initializing',
        )

    def handle_message(self, message):
        if message.id in self.persisted_messages:
            self.queue.delete_message(message)
            return None

        if message.id in self.active_messages:
            return None

        message_body = message.get_body()

        try:
            message_data = json.loads(message_body)
        except ValueError:
            self.log(
                event='handle_message',
                error='Unable to parse JSON message',
            )
            self.queue.delete_message(message)
            return None

        if type(message_data) is not dict:
            self.log(
                view='aggregator',
                event='handle_message',
                error='No data dictionary found',
            )
            self.queue.delete_message(message)
            return None

        if 'daterecorded' not in message_data:
            self.log(
                event='handle_message',
                error='Could not locate daterecorded field',
            )
            self.queue.delete_message(message)
            return None

        if type(message_data['daterecorded']) is not long:
            self.log(
                event='handle_message',
                error='%s is not an valid timestamp' % (message_data['daterecorded'],),
            )
            self.queue.delete_message(message)
            return None

        self.active_messages[message.id] = message
        message_date = message_data['daterecorded']

        for duration_label, duration_time in self.log_durations:

            message_date_offset = message_date % duration_time
            block_key = message_date - message_date_offset
            self.blocks[duration_label][block_key][message.id] = message_data

    def handle_blocks(self):
        start = time.time()

        pool = Pool(settings.THREADPOOL_SIZE)
        for duration_label, duration_time in self.log_durations:
            for block_key in self.blocks[duration_label].keys():
                block_data = self.blocks[duration_label][block_key].values()

                for handler in self.handlers:
                    pool.apply_async(handler.handle, (duration_label, block_key, block_data))

        pool.close()
        pool.join()

        self.last_handled_date = datetime.datetime.now()

        end = time.time()
        self.log(
            event='handle_blocks',
            count=len(self.active_messages),
            time=(end - start),
        )

    def delete_blocks(self):
        start = time.time()

        active_messages = self.active_messages.values()
        active_message_ids = self.active_messages.keys()

        if active_messages:
            message_batches = group_by(active_messages, 10)

            pool = Pool(settings.THREADPOOL_SIZE)

            pool.map(self.queue.delete_message_batch, message_batches)

            pool.close()
            pool.join()

        self.active_messages = {}
        self.persisted_messages = set(active_message_ids)
        self.blocks = defaultdict(lambda: defaultdict(dict))

        end = time.time()

        self.log(
            event='delete_messages',
            count=len(self.persisted_messages),
            time=(end - start),
        )

    def receive_messages(self):
        try:
            messages = self.queue.get_messages(num_messages=10)
        except SQSError, e:
            self.log(
                event='receive_messages',
                error=str(e),
            )
            time.sleep(1)
            return None

        if not messages:
            time.sleep(1)

        for message in messages:
            self.handle_message(message)

    def should_handle_blocks(self):
        now = datetime.datetime.now()
        elapsed = (now - self.last_handled_date).seconds * 1000
        return elapsed > self.persist_duration

    def run(self):
        while True:
            self.receive_messages()

            if self.should_handle_blocks():
                self.handle_blocks()
                self.delete_blocks()


class Command(BaseCommand):
    help = 'Aggregate Readings from a queue and persist them to S3'

    def handle(self, *args, **options):
        public_bucket = get_bucket(settings.S3_PUBLIC_BUCKET)
        private_bucket = get_bucket(settings.S3_PRIVATE_BUCKET)

        public_s3_handler = S3FilteredHandler(
            bucket=public_bucket,
            input_path='pressure/raw/',
            output_path='pressure/raw/',
            allowed_fields=ReadingListSerializer.Meta.fields
        )

        private_s3_handler = S3Handler(
            bucket=private_bucket,
            input_path='pressure/raw/',
            output_path='pressure/raw/',
        )

        dynamodb_conn = get_conn()
        statistics_table = dynamodb_conn.get_table(settings.DYNAMODB_TABLE)
        public_dynamodb_handler = DynamoDBHandler(
            conn=dynamodb_conn,
            table=statistics_table,
            bucket=private_bucket,
            input_path='pressure/raw/',
        )

        queue = get_queue(settings.SQS_QUEUE)
        aggregator = QueueAggregator(
            queue=queue,
            handlers=(
                public_s3_handler,
                private_s3_handler,
                public_dynamodb_handler,
            ),
            persist_duration=settings.LOG_PERSIST_DURATION,
            log_durations=settings.LOG_DURATIONS,
        )

        aggregator.run()
