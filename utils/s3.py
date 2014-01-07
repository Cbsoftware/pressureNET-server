from django.conf import settings
from django.utils import simplejson as json

from boto.exception import BotoServerError
from boto.s3.connection import S3Connection
from boto.s3.key import Key


s3_conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)

def get_bucket(bucket_name):
    try:
        return s3_conn.get_bucket(bucket_name)
    except BotoServerError:
        return None


def write_to_bucket(bucket, key, content, content_type):
    try:
        s3_file = Key(bucket)
        s3_file.key = str(key)
        s3_file.content_type = content_type

        s3_data = content 
        s3_file.set_contents_from_string(s3_data)

        return s3_file
    except BotoServerError:
        return None
