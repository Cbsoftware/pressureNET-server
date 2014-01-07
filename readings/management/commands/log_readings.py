import datetime
import time
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import simplejson as json

from readings.serializers import ReadingListSerializer

from utils.time_utils import to_unix, from_unix
from utils.compression import gzip_compress, gzip_decompress
from utils.loggly import loggly
from utils.queue import get_queue
from utils.s3 import get_bucket, read_from_bucket, write_to_bucket


def hash_dict(data):
    return hash(''.join([str(value) for value in data.values()]))


class S3Handler(object):

    def __init__(self, bucket, allowed_fields=None):
        self.bucket = bucket
        self.allowed_fields = allowed_fields

    def filter_data(self, data):
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

    def merge_data(self, data1, data2):
        print 'Merging %s and %s readings' % (
            len(data1),
            len(data2),
        )
        dict1 = dict([(hash_dict(record), record) for record in data1])
        dict2 = dict([(hash_dict(record), record) for record in data2])

        dict1.update(dict2)

        print 'Merged %s readings' % (len(dict1),)
        return dict1.values()

    def handle(self, key, new_messages):
        print 'Persisting %s to S3' % (key,)
        filename = '%s.json' % (key,)

        new_data = [json.loads(message.get_body()) for message in new_messages]
        filtered_data = self.filter_data(new_data)

        existing_content = read_from_bucket(self.bucket, filename)
        if existing_content:
            print 'Existing data found, merging'
            existing_data = json.loads(existing_content)

            filtered_data = self.merge_data(filtered_data, existing_data)

        output_content = json.dumps(filtered_data)
        write_to_bucket(
            self.bucket,
            filename,
            output_content,
            'application/json',
            compress=True,
        )

        print 'Persisted %s messages from %s to %s' % (
            len(filtered_data),
            from_unix(key),
            self.bucket,
        )


class QueueAggregator(object):

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
            print 'Unable to parse JSON message'
            self.queue.delete_message(message)
            return None

        if type(message_data) is not dict:
            print 'No data dictionary found'
            self.queue.delete_message(message)
            return None

        if 'daterecorded' not in message_data:
            print 'Could not locate daterecorded field'
            self.queue.delete_message(message)
            return None

        message_date = int(message_data['daterecorded'])
        message_date_offset = message_date % settings.READINGS_LOG_DURATION
        block_key = message_date - message_date_offset

        if message.id in self.persisted_messages:
            print 'Received duplicate message from ', from_unix(block_key)
            self.queue.delete_message(message)
            return None

        self.blocks[block_key][message.id] = message

    def handle_block(self, block_key):
        print 'Handling block', block_key
        for handler in self.handlers:
            handler.handle(block_key, self.blocks[block_key].values())
        print 'Handled block', block_key

        self.delete_block(block_key)

    def delete_block(self, block_key):
        print 'Deleting block', block_key
        while self.blocks[block_key]:
            messages = self.blocks[block_key].values()[:10]
            response = self.queue.delete_message_batch(messages)

            for deleted_reading in response.results:
                deleted_id = deleted_reading['id']
                del self.blocks[block_key][deleted_id]
                self.persisted_messages.add(deleted_id)

        del self.blocks[block_key]
        print 'Deleted block', block_key

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
        print 'Persisted %s messages' % (len(self.persisted_messages),)

    def run(self):
        while True:
            self.receive_messages()

            if self.should_handle_blocks():
                self.handle_blocks()


class Command(BaseCommand):
    help = 'Aggregate Readings from a queue and persist them to S3'

    def handle(self, *args, **options):
        public_bucket = get_bucket(settings.S3_PUBLIC_BUCKET)
        public_handler = S3Handler(
            public_bucket,
            allowed_fields=ReadingListSerializer.Meta.fields
        )

        private_bucket = get_bucket(settings.S3_PRIVATE_BUCKET)
        private_handler = S3Handler(private_bucket)

        queue = get_queue(settings.SQS_QUEUE)
        aggregator = QueueAggregator(
            queue,
            handlers=(
                public_handler,
                private_handler
            ),
        )

        aggregator.run()
