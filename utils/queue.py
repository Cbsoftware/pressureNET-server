from django.conf import settings
from django.utils import simplejson as json

from boto.exception import BotoServerError
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message

from utils.loggly import loggly


sqs_conn = SQSConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)

def get_queue(queue_name):
    try:
        return sqs_conn.get_queue(queue_name)
    except BotoServerError:
        return None


def add_to_queue(queue, data):
    message = Message()
    message.set_body(json.dumps(data))

    try:
        return queue.write(message)
    except BotoServerError:
        return None
