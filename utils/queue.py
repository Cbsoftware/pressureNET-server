from django.conf import settings
from django.utils import simplejson as json

from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message

from utils.loggly import loggly


sqs_conn = SQSConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)

def get_queue(queue_name):
    return sqs_conn.get_queue(queue_name)

def add_to_queue(queue, data):
    message = Message()
    message.set_body(json.dumps(data))
    return queue.write(message)
