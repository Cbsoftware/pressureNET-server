import datetime
import math
import time
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import simplejson as json

from boto.exception import SQSError

from readings.serializers import ReadingListSerializer

from utils.time_utils import to_unix, from_unix
from utils.compression import gzip_compress, gzip_decompress
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


# handlers
class S3Handler(Logger):

    def __init__(self, bucket=None, input_path=None, output_path=None):
        self.bucket = bucket
        self.input_path = input_path
        self.output_path = output_path

    def merge_data(self, existing_data, new_data):
        existing_dict = dict([(hash_dict(record), record) for record in existing_data])
        new_dict = dict([(hash_dict(record), record) for record in new_data])

        existing_dict.update(new_dict)

        return existing_dict.values()

    def process_data(self, data):
        return data

    def handle(self, duration_label, key, data):
        input_file = '%s%s/%s.json' % (self.input_path, duration_label, key)
        output_file = '%s%s/%s.json' % (self.output_path, duration_label, key)

        existing_content = read_from_bucket(self.bucket, input_file)
        if existing_content:
            existing_data = json.loads(existing_content)
            data = self.merge_data(existing_data, data)

        processed_data = self.process_data(data)

        output_content = json.dumps(processed_data)

        write_to_bucket(
            self.bucket,
            output_file,
            output_content,
            'application/json',
            compress=True,
        )

        self.log(
            event='write to s3',
            filename=output_file,
            bucket=str(self.bucket),
            messages=len(processed_data),
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


class S3StatisticHandler(S3Handler):

    def process_data(self, data):
        geo_sorted = defaultdict(list)

        for data_point in data:
            geo_key = geohash.encode(
                data_point['latitude'],
                data_point['longitude'],
                precision=5,
            )
            geo_sorted[geo_key].append(data_point)

        statistics = {}

        for geo_key, data_points in geo_sorted.items():
            readings = [data_point['reading'] for data_point in data_points]
            statistics[geo_key] = {
                'min': min(readings),
                'max': max(readings),
                'mean': mean(readings),
                'median': median(readings),
                'std_dev': std_dev(readings),
                'samples': len(readings),
            }

        return statistics


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
            self.log(
                event='handle_message',
                error='Received deleted message',
            )
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

    def handle_block(self, duration_label, block_key):
        block_data = self.blocks[duration_label][block_key].values()

        for handler in self.handlers:
            handler.handle(duration_label, block_key, block_data)

    def handle_blocks(self):
        for duration_label, duration_time in self.log_durations:
            for block_key in self.blocks[duration_label].keys():
                self.handle_block(duration_label, block_key)

        self.last_handled_date = datetime.datetime.now()
        self.log(
            event='handle_blocks',
            count=len(self.active_messages),
        )

    def delete_blocks(self):
        start = time.time()

        self.persisted_messages = set()

        while self.active_messages:
            messages = self.active_messages.values()[:10]
            response = self.queue.delete_message_batch(messages)

            for deleted in response.results:
                deleted_id = deleted['id']

                self.active_messages.pop(deleted_id)
                self.persisted_messages.add(deleted_id)

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
            try:
                self.receive_messages()

                if self.should_handle_blocks():
                    self.handle_blocks()
                    self.delete_blocks()
            except Exception, e:
                self.log(
                    error=str(e),
                )


class Command(BaseCommand):
    help = 'Aggregate Readings from a queue and persist them to S3'

    def handle(self, *args, **options):
        public_bucket = get_bucket(settings.S3_PUBLIC_BUCKET)
        private_bucket = get_bucket(settings.S3_PRIVATE_BUCKET)

        public_handler = S3FilteredHandler(
            bucket=public_bucket,
            input_path='pressure/raw/',
            output_path='pressure/raw/',
            allowed_fields=ReadingListSerializer.Meta.fields
        )

        public_stat_handler = S3StatisticHandler(
            bucket=public_bucket,
            input_path='pressure/raw/',
            output_path='pressure/statistics/',
        )

        private_handler = S3Handler(
            bucket=private_bucket,
            input_path='pressure/raw/',
            output_path='pressure/raw/',
        )

        queue = get_queue(settings.SQS_QUEUE)
        aggregator = QueueAggregator(
            queue=queue,
            handlers=(
                public_handler,
                public_stat_handler,
                private_handler,
            ),
            persist_duration=settings.LOG_PERSIST_DURATION,
            log_durations=settings.LOG_DURATIONS,
        )

        aggregator.run()
