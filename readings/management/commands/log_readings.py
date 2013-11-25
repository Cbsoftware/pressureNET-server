from collections import defaultdict
import datetime
import time

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import simplejson as json

from boto.sqs.connection import SQSConnection

from utils.time_utils import to_unix, from_unix

LOG_DURATION = 2 * 60 * 1000

def group_by(items, length):
    while items:
        yield items[:length]
        items = items[length:]

class Command(BaseCommand):
    help = 'Checks code for errors'

    def handle(self, *args, **options):
        conn = SQSConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        queue = conn.get_queue('pressurenet-readings-dev')

        reading_logs = defaultdict(dict)
        removed_messages = {}

        while True:
            reading_messages = queue.get_messages(num_messages=10)

            if not reading_messages:
                time.sleep(1)

            for reading_message in reading_messages:
                reading_body = reading_message.get_body()

                try:
                    reading_json = json.loads(reading_body)
                except:
                    queue.delete_message(reading_message)
                    continue

                reading_date = reading_json['daterecorded']
                reading_date_offset = reading_date % LOG_DURATION
                reading_date_block = reading_date - reading_date_offset
                
                if reading_message.id in removed_messages:
                    print 'Received duplicate message from ', from_unix(reading_date_block)
                    queue.delete_message(reading_message)
                    continue

                reading_logs[reading_date_block][reading_message.id] = reading_message

            for log_block in reading_logs.keys():
                block_startdate = from_unix(log_block)

                if (datetime.datetime.now() - block_startdate).seconds > (2 * (LOG_DURATION/1000.0)):
                    print 'Persisting %s messages from %s to s3' % (
                        len(reading_logs[log_block]),
                        block_startdate,
                    )

                    while reading_logs[log_block].values():
                        response = queue.delete_message_batch(reading_logs[log_block].values()[:10])

                        for deleted_reading in response.results:
                            del reading_logs[log_block][deleted_reading['id']]
                            removed_messages[deleted_reading['id']] = True

                    del reading_logs[log_block]
