from collections import defaultdict
import datetime
import time

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import simplejson as json

from readings.serializers import ReadingListSerializer

from utils.time_utils import to_unix, from_unix
from utils.loggly import loggly
from utils.queue import get_queue, get_from_queue
from utils.s3 import get_bucket, write_to_bucket


class ReadingQueueAggregator(object):

    def __init__(self):
        self.queue = get_queue()
        self.public_bucket = get_bucket(settings.S3_PUBLIC_BUCKET)
        self.private_bucket = get_bucket(settings.S3_PRIVATE_BUCKET)
        self.reading_blocks = defaultdict(dict)
        self.removed_messages = {}

    def is_expired(self, timestamp):
        now = datetime.datetime.now()
        threshold = 2 * settings.READINGS_LOG_DURATION
        diff = (now - from_unix(timestamp)).seconds * 1000
        return diff > threshold

    def handle_message(self, reading_message):
        reading_body = reading_message.get_body()

        try:
            reading_json = json.loads(reading_body)
        except ValueError:
            print 'Unable to parse JSON message'
            self.queue.delete_message(reading_message)
            return None

        if type(reading_json) is not dict:
            print 'No data dictionary found'
            self.queue.delete_message(reading_message)
            return None

        if 'daterecorded' not in reading_json:
            print 'Could not locate daterecorded field'
            self.queue.delete_message(reading_message)
            return None

        reading_date = int(reading_json['daterecorded'])
        reading_date_offset = reading_date % settings.READINGS_LOG_DURATION
        block_key = reading_date - reading_date_offset
     
        if self.is_expired(block_key):
            print 'Received expired message from ', from_unix(block_key)
            self.queue.delete_message(reading_message)
            return None

        self.reading_blocks[block_key][reading_message.id] = reading_message

    def get_block_filename(self, block_key):
        return block_key

    def persist_block_public(self, block_key):
        s3_key = self.get_block_filename(block_key)
        public_data = []

        for message in self.reading_blocks[block_key].values():
            message_data = json.loads(message.get_body())

            filtered_data = dict([
                (key, value) for (key, value) in message_data.items() 
                    if key in ReadingListSerializer.Meta.fields
            ])

            public_data.append(filtered_data)

        s3_data = json.dumps(public_data)
        return write_to_bucket(self.public_bucket, s3_key, s3_data, 'application/json')
    
    def delete_block(self, block_key):
        while self.reading_blocks[block_key].values():
            response = self.queue.delete_message_batch(self.reading_blocks[block_key].values()[:10])

            for deleted_reading in response.results:
                del self.reading_blocks[block_key][deleted_reading['id']]
                self.removed_messages[deleted_reading['id']] = True

        del self.reading_blocks[block_key]

    def persist_block_private(self, block_key):
        s3_key = self.get_block_filename(block_key)
        s3_data = json.dumps([
            json.loads(message.get_body()) for message in self.reading_blocks[block_key].values()
        ])
        return write_to_bucket(self.private_bucket, s3_key, s3_data, 'application/json')

    def handle_block(self, block_key):
        public_success = self.persist_block_public(block_key)
        private_success = self.persist_block_private(block_key)

        if public_success and private_success:
            print 'Persisting %s messages from %s to s3' % (
                len(self.reading_blocks[block_key]),
                from_unix(block_key),
            )

            self.delete_block(block_key)

    def receive_messages(self):
        reading_messages = get_from_queue() 

        if not reading_messages:
            time.sleep(1)

        for reading_message in reading_messages:
            self.handle_message(reading_message)

    def persist_data(self):
        for block_key in self.reading_blocks.keys():
            if self.is_expired(block_key):
                self.handle_block(block_key)

    def run(self):
        while True:
            self.receive_messages()
            self.persist_data()


class Command(BaseCommand):
    help = 'Aggregate Readings from a queue and persist them to S3'

    def handle(self, *args, **options):
        aggregator = ReadingQueueAggregator()
        aggregator.run()
