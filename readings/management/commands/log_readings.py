import datetime
import math
import time
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import simplejson as json


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

        self.log(
            event='merge',
            existing_data=len(existing_data),
            new_data=len(new_data),
            merged=len(existing_dict),
        )

        return existing_dict.values()

    def process_data(self, data):
        return data

    def handle(self, key, data):
        input_file = '%s%s.json' % (self.input_path, key)
        output_file = '%s%s.json' % (self.output_path, key)

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
            if len(readings) == 2:
                import pdb
                pdb.set_trace()
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

    def __init__(self, queue, handlers=None):
        self.queue = queue
        self.blocks = defaultdict(dict)
        self.handlers = handlers
        self.persisted_messages = set()
        self.last_handled_date = datetime.datetime.now()

    def handle_message(self, message):
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

        message_date = int(message_data['daterecorded'])
        message_date_offset = message_date % settings.READINGS_LOG_DURATION
        block_key = message_date - message_date_offset

        if message.id in self.persisted_messages:
            self.log(
                event='handle_message',
                error='Received duplicate message from %s' % (from_unix(block_key),),
            )
            self.queue.delete_message(message)
            return None

        self.blocks[block_key][message.id] = message

    def handle_block(self, block_key):
        block_messages = self.blocks[block_key].values()
        block_data = [json.loads(message.get_body()) for message in block_messages]
        for handler in self.handlers:
            handler.handle(block_key, block_data)

        self.delete_block(block_key)

    def delete_block(self, block_key):
        while self.blocks[block_key]:
            messages = self.blocks[block_key].values()[:10]
            response = self.queue.delete_message_batch(messages)

            for deleted_reading in response.results:
                deleted_id = deleted_reading['id']
                del self.blocks[block_key][deleted_id]
                self.persisted_messages.add(deleted_id)

        del self.blocks[block_key]

    def receive_messages(self):
        messages = self.queue.get_messages(num_messages=10)

        if not messages:
            time.sleep(1)

        for message in messages:
            self.handle_message(message)

    def should_handle_blocks(self):
        now = datetime.datetime.now()
        elapsed = (now - self.last_handled_date).seconds * 1000
        return elapsed > settings.READINGS_LOG_DURATION

    def handle_blocks(self):
        self.persisted_messages = set()

        for block_key in self.blocks.keys():
            self.handle_block(block_key)

        self.last_handled_date = datetime.datetime.now()
        self.log(
            event='handle_blocks',
            count=len(self.persisted_messages),
        )

    def run(self):
        while True:
            self.receive_messages()

            if self.should_handle_blocks():
                self.handle_blocks()


class Command(BaseCommand):
    help = 'Aggregate Readings from a queue and persist them to S3'

    def handle(self, *args, **options):
        public_bucket = get_bucket(settings.S3_PUBLIC_BUCKET)
        public_handler = S3FilteredHandler(
            bucket=public_bucket,
            input_path='pressure/raw/10minute/',
            output_path='pressure/raw/10minute/',
            allowed_fields=ReadingListSerializer.Meta.fields
        )

        public_stat_handler = S3StatisticHandler(
            bucket=public_bucket,
            input_path='pressure/raw/10minute/',
            output_path='pressure/statistics/10minute/',
        )

        private_bucket = get_bucket(settings.S3_PRIVATE_BUCKET)
        private_handler = S3Handler(
            bucket=private_bucket,
            input_path='pressure/raw/10minute/',
            output_path='pressure/raw/10minute/',
        )

        queue = get_queue(settings.SQS_QUEUE)
        aggregator = QueueAggregator(
            queue,
            handlers=(
                public_handler,
                public_stat_handler,
                private_handler,
            ),
        )

        aggregator.run()
