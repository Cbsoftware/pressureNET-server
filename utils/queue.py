from django.conf import settings
from django.utils import simplejson as json

from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message


sqs_conn = SQSConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)

def get_queue():
    return sqs_conn.get_queue(settings.SQS_QUEUE)

def add_to_queue(data):
    queue = get_queue()
    message = Message()
    message.set_body(json.dumps(data))
    return queue.write(message)
    
def get_from_queue(num_messages=10):
    queue = get_queue()
    return queue.get_messages(num_messages=10)
