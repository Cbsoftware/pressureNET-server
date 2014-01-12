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

def merge_datasets(*datasets):
    result = {}

    for dataset in datasets:
        hashed_dataset = dict([(hash_dict(record), record) for record in dataset])
        result.update(hashed_dataset) 

    return result.values()


# handlers
class S3Handler(Logger):

    def __init__(self, bucket=None, input_path=None, output_path=None):
        self.bucket = bucket
        self.input_path = input_path
        self.output_path = output_path

    def process_data(self, data):
        return data

    def handle(self, key, data):
        input_file = '%s%s.json' % (self.input_path, key)
        output_file = '%s%s.json' % (self.output_path, key)

        existing_content = read_from_bucket(self.bucket, input_file)
        if existing_content:
            existing_data = json.loads(existing_content)
            data = merge_datasets(existing_data, data)

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


class RawAggregator(Logger):

    def __init__(self, duration=None, handlers=None):
        self.duration = duration
        self.handlers = handlers

        self.blocks = defaultdict(dict)
        self.completed_messages = set()
        self.last_handled_date = datetime.datetime.now()

    def handle_message(self, message):
        if message.id in self.completed_messages:
            return None

        message_body = message.get_body()

        try:
            message_data = json.loads(message_body)
        except ValueError:
            self.log(
                event='handle_message',
                error='Unable to parse JSON message',
            )
            self.completed_messages.add(message.id)
            return None

        if type(message_data) is not dict:
            self.log(
                view='aggregator',
                event='handle_message',
                error='No data dictionary found',
            )
            self.completed_messages.add(message.id)
            return None

        if 'daterecorded' not in message_data:
            self.log(
                event='handle_message',
                error='Could not locate daterecorded field',
            )
            self.completed_messages.add(message.id)
            return None

        if type(message_data['daterecorded']) is not long:
            self.log(
                event='handle_message',
                error='%s is not an valid timestamp' % (message_data['daterecorded'],),
            )
            self.completed_messages.add(message.id)
            return None

        message_date = int(message_data['daterecorded'])
        message_date_offset = message_date % self.duration
        block_key = message_date - message_date_offset
        self.blocks[block_key][message.id] = message

    def handle_block(self, block_key):
        block_messages = self.blocks[block_key].values()
        block_data = [json.loads(message.get_body()) for message in block_messages]

        for handler in self.handlers:
            handler.handle(block_key, block_data)

        self.delete_block(block_key)

    def delete_block(self, block_key):
        messages = self.blocks[block_key].values()
        message_ids = [message.id for message in messages]
        self.completed_messages = self.completed_messages.union(set(message_ids))
        self.blocks.pop(block_key)

    def should_handle_blocks(self):
        now = datetime.datetime.now()
        elapsed = (now - self.last_handled_date).seconds * 1000
        return elapsed > self.duration

    def handle_blocks(self):
        block_keys = []
        if self.should_handle_blocks():
            block_keys = self.blocks.keys()
            for block_key in block_keys:
                self.handle_block(block_key)

            self.last_handled_date = datetime.datetime.now()
            self.log(
                event='handle_blocks',
                count=len(self.completed_messages),
            )

        return block_keys

    def remove_message(self, message_id):
        self.completed_messages.remove(message_id)


class RollupAggregator(Logger):

    def __init__(self, input_bucket=None, input_path=None, duration=None, handlers=None):
        self.input_bucket = input_bucket
        self.input_path = input_path
        self.duration = duration
        self.handlers = handlers

        self.blocks = defaultdict(set)
        self.last_handled_date = datetime.datetime.now()

    def handle_message(self, input_block_key):
        input_block_key_offset = input_block_key % self.duration
        output_block_key = input_block_key - input_block_key_offset
        self.blocks[output_block_key].add(input_block_key)

    def handle_block(self, output_block_key):
        input_block_keys = self.blocks[output_block_key]
        all_input_datasets = []

        for input_block_key in input_block_keys:
            input_file = '%s%s.json' % (self.input_path, input_block_key)
            input_content = read_from_bucket(self.input_bucket, input_file)
            input_dataset = json.loads(input_content)
            all_input_datasets.append(input_dataset)

        output_block_data = merge_datasets(*all_input_datasets) 

        for handler in self.handlers:
            handler.handle(output_block_key, output_block_data)

        self.delete_block(output_block_key)

    def delete_block(self, block_key):
        self.blocks.pop(block_key)

    def should_handle_blocks(self):
        now = datetime.datetime.now()
        elapsed = (now - self.last_handled_date).seconds * 1000
        return elapsed > self.duration

    def handle_blocks(self):
        if self.should_handle_blocks():
            block_keys = self.blocks.keys()
            for block_key in block_keys:
                self.handle_block(block_key)

            self.last_handled_date = datetime.datetime.now()
            self.log(
                event='handle_blocks',
                count=len(block_keys),
            )


class QueueHandler(Logger):

    def __init__(self, queue, aggregator, rollups):
        self.queue = queue
        self.aggregator = aggregator
        self.rollups = rollups
        self.active_messages = {}
        self.deleted_messages = set()

    def receive_messages(self):
        messages = self.queue.get_messages(num_messages=10)

        if not messages:
            time.sleep(1)

        for message in messages:
            if message.id in self.deleted_messages:
                self.queue.delete_message(message)

            elif message.id not in self.active_messages:
                self.active_messages[message.id] = message
                self.aggregator.handle_message(message)

    def handle_blocks(self):
        handled_block_keys = self.aggregator.handle_blocks()

        for handled_block_key in handled_block_keys:
            for rollup in self.rollups:
                rollup.handle_message(handled_block_key)

        for rollup in self.rollups:
            rollup.handle_blocks()

    def delete_messages(self):
        completed_message_ids = set(self.aggregator.completed_messages)

        if completed_message_ids:
            self.deleted_messages = set()

            for completed_message_id in completed_message_ids:
                completed_message = self.active_messages[completed_message_id]

                self.queue.delete_message(completed_message)

                self.deleted_messages.add(completed_message_id)
                self.active_messages.pop(completed_message_id)

                self.aggregator.remove_message(completed_message_id)

            self.log(
                event='deleted_messages',
                count=len(completed_message_ids),
            )

    def run(self):
        while True:
            self.receive_messages()
            self.handle_blocks()
            self.delete_messages()


class Command(BaseCommand):
    help = 'Aggregate Readings from a queue and persist them to S3'

    def handle(self, *args, **options):
        public_bucket = get_bucket(settings.S3_PUBLIC_BUCKET)
        private_bucket = get_bucket(settings.S3_PRIVATE_BUCKET)

        log_duration_label, log_duration_time = settings.LOG_DURATIONS

        public_handler = S3FilteredHandler(
            bucket=public_bucket,
            input_path='pressure/raw/%s/' % (log_duration_label,),
            output_path='pressure/raw/%s/' % (log_duration_label,),
            allowed_fields=ReadingListSerializer.Meta.fields
        )

        public_stat_handler = S3StatisticHandler(
            bucket=public_bucket,
            input_path='pressure/raw/%s/' % (log_duration_label,),
            output_path='pressure/statistics/%s/' % (log_duration_label,),
        )

        private_handler = S3Handler(
            bucket=private_bucket,
            input_path='pressure/raw/%s/' % (log_duration_label,),
            output_path='pressure/raw/%s/' % (log_duration_label,),
        )

        aggregator = RawAggregator(
            duration=log_duration_time,
            handlers=(
                public_handler,
                public_stat_handler,
                private_handler,
            ),
        )

        rollups = []
        for rollup_duration_label, rollup_duration_time in settings.ROLLUP_DURATIONS:
            
            public_handler = S3FilteredHandler(
                bucket=public_bucket,
                input_path='pressure/raw/%s/' % (rollup_duration_label,),
                output_path='pressure/raw/%s/' % (rollup_duration_label,),
                allowed_fields=ReadingListSerializer.Meta.fields
            )

            public_stat_handler = S3StatisticHandler(
                bucket=public_bucket,
                input_path='pressure/raw/%s/' % (rollup_duration_label,),
                output_path='pressure/statistics/%s/' % (rollup_duration_label,),
            )

            private_handler = S3Handler(
                bucket=private_bucket,
                input_path='pressure/raw/%s/' % (rollup_duration_label,),
                output_path='pressure/raw/%s/' % (rollup_duration_label,),
            )

            rollup = RollupAggregator(
                input_bucket=private_bucket,
                input_path='pressure/raw/%s/' % (log_duration_label,),
                duration=rollup_duration_time,
                handlers=(
                    public_handler,
                    public_stat_handler,
                    private_handler,
                ),
            )

            rollups.append(rollup)


        queue = get_queue(settings.SQS_QUEUE)
        self.queue_handler = QueueHandler(
            queue,
            aggregator=aggregator,
            rollups=rollups,
        )

        self.queue_handler.run()
