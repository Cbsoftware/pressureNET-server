from django.conf import settings
from django.utils import simplejson as json

from boto.exception import BotoServerError
from boto.s3.connection import S3Connection
from boto.s3.key import Key

from utils.compression import gzip_compress, gzip_decompress


s3_conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)


def get_bucket(bucket_name):
    try:
        return s3_conn.get_bucket(bucket_name)

    except BotoServerError:
        return None


def read_from_bucket(bucket, filename):
    try:
        key = bucket.get_key(filename)

        if key:
            content = key.get_contents_as_string()

            if key.content_encoding == 'gzip':
                content = gzip_decompress(content)

            return content

    except BotoServerError:
        return None


def write_to_bucket(bucket, key, content, content_type='', content_encoding='', compress=False):
    try:
        s3_file = Key(bucket)
        s3_file.key = str(key)

        if compress:
            content = gzip_compress(content)
            content_encoding = 'gzip'

        s3_file.set_contents_from_string(
            content,
            headers={
                'Content-Type': content_type,
                'Content-Encoding': content_encoding,
            },
        )

        return s3_file

    except BotoServerError:
        return None
