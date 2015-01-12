import StringIO
import csv
import pickle
import time
import traceback
import uuid
from collections import defaultdict

import redis as pyredis
from celery import Celery
from django.conf import settings
from django.utils import simplejson as json
from django.utils.functional import cached_property

from readings import choices as readings_choices
from readings.serializers import ReadingListSerializer

from utils.dynamodb import get_conn, write_items
from utils.loggly import Logger
from utils.s3 import get_bucket, read_from_bucket, write_to_bucket
from utils.statistics import mean, median, std_dev
from utils import geohash


app = Celery('PressureNET')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')


# GLobal constants
REDIS = pyredis.StrictRedis(host=settings.REDIS_URL)
ALL_SHARING_LABELS = [choice[0] for choice in readings_choices.SHARING_CHOICES]


# Utility functions
def hash_dict(data):
    return '%s%s%s' % (
        data['latitude'],
        data['longitude'],
        data['daterecorded'],
    )


def group_by(items, length):
    while items:
        yield items[:length]
        items = items[length:]


def is_block_key(block_key):
    return block_key.startswith('block:')


def get_block_key(duration, block):
    return 'block:%s:%s' % (duration, block)


def unpack_block_key(block_key):
    return block_key.split(':')[1:]


def get_file_path(format, duration, block, path_prefix=''):
    return 'readings/pressure/{prefix}/{format}/{duration}/{block}.{format}'.format(
        prefix=path_prefix,
        format=format,
        duration=duration,
        block=block,
    )


# Base Task
class BaseTask(app.Task, Logger):

    def handle(self, *args, **kwargs):
        raise NotImplementedError

    def run(self, *args, **kwargs):
        start = time.time()
        success = False

        try:
            log_info = self.handle(*args, **kwargs)
            success = True
        except Exception, e:
            log_info = {
                'error': str(e),
                'traceback': str(traceback.format_exc()),
            }

        end = time.time()

        self.log(
            success=success,
            time=(end - start),
            redis_memory=REDIS.info()['used_memory_human'],
            **(log_info or {})
        )


# Writers
class BaseS3Writer(BaseTask):

    def prepare(self, data):
        raise NotImplementedError

    def write(self, bucket_name, output_path, output_content):
        write_to_bucket(
            get_bucket(bucket_name),
            output_path,
            output_content,
            'application/{format}'.format(format=self.file_format),
            compress=True,
        )

    def handle(self, bucket_name, output_path, data):
        output_content = self.prepare(data)
        self.write(bucket_name, output_path, output_content)

        return {
            'format': self.file_format,
            'count': len(data),
            'bucket': bucket_name,
            'output_path': output_path,
        }


class JSONS3Writer(BaseS3Writer):
    file_format = 'json'

    def prepare(self, data):
        return json.dumps(data)


class CSVS3Writer(BaseS3Writer):
    file_format = 'csv'

    def prepare(self, data):
        output = StringIO.StringIO()
        writer = csv.writer(output)

        labels = data[0].keys()
        writer.writerow(labels)

        for row in data:
            writer.writerow(row.values())

        output_content = output.getvalue()
        output.close()

        return output_content


# Handlers
class DataHandler(BaseTask):
    bucket = None
    read_sharing_type = 'combined'
    read_sharing_label = readings_choices.SHARING_PRIVATE

    def load_block_data(self, block_key):
        block_data = REDIS.lrange(block_key, 0, -1)
        return [pickle.loads(datum) for datum in block_data]

    def merge_data(self, existing_data, new_data):
        existing_dict = dict(
            [(hash_dict(record), record) for record in existing_data])
        new_dict = dict([(hash_dict(record), record) for record in new_data])

        existing_dict.update(new_dict)

        return existing_dict.values()

    def load_existing_data(self, duration, block):
        path_prefix = '{type}/{label}'.format(
            type=self.read_sharing_type,
            label=self.read_sharing_label
        )
        input_file = get_file_path(
            'json',
            duration,
            block,
            path_prefix=path_prefix
        )

        existing_content = read_from_bucket(
            get_bucket(self.bucket),
            input_file,
        )
        if existing_content:
            return json.loads(existing_content)

    def process_data(self, data):
        return data

    def write_data(self, duration, block, data):
        raise NotImplementedError

    def handle(self, block_key, duration, block):
        new_data = self.load_block_data(block_key)

        existing_data = self.load_existing_data(duration, block)

        if existing_data:
            all_data = self.merge_data(existing_data, new_data)
        else:
            all_data = new_data

        processed_data = self.process_data(all_data)

        self.write_data(duration, block, processed_data)

        return {
            'duration': duration,
            'block': block,
            'new_data': len(new_data),
            'existing_data': len(existing_data) if existing_data else 0,
            'merged_data': len(all_data),
            'processed_data': len(processed_data),
            'bucket': self.bucket,
        }


class S3Handler(DataHandler):
    durations = reduce(set.union, map(set, settings.LOG_DURATIONS.values()))
    sharing_durations = settings.LOG_DURATIONS
    writers = [
        JSONS3Writer,
        CSVS3Writer,
    ]

    def write_data(self, duration, block, data):
        for writer in self.writers:
            output_path = get_file_path(writer.file_format, duration, block)
            writer().delay(self.bucket, output_path, data)


class S3SharingHandler(S3Handler):

    def write_data(self, duration, block, data):
        for sharing_type, sharing_label_groups in self.sharing_types.items():
            if duration in self.sharing_durations[sharing_type]:
                for sharing_labels in sharing_label_groups:
                    filtered_data = [
                        datum for datum in data
                        if datum['sharing'] in sharing_labels
                    ]

                    if filtered_data:
                        path_label = sharing_labels[-1]
                        path_prefix = '{type}/{label}'.format(
                            type=sharing_type,
                            label=path_label
                        )

                        for writer in self.writers:
                            output_path = get_file_path(
                                writer.file_format,
                                duration,
                                block,
                                path_prefix=path_prefix
                            )
                            writer().delay(self.bucket, output_path, filtered_data)


class S3FieldFilteredHandler(S3SharingHandler):

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


class S3UserHandler(S3Handler):
    durations = ('daily',)

    def write_data(self, duration, block, data):
        user_ids = set([datum['user_id'] for datum in data])
        for user_id in user_ids:
            user_data = [datum for datum in data if datum['user_id'] == user_id]
            path_prefix = 'user/{user_id}'.format(user_id=user_id)

            for writer in self.writers:
                output_path = get_file_path(
                    writer.file_format,
                    duration,
                    block,
                    path_prefix=path_prefix
                )
                writer().delay(self.bucket, output_path, user_data)


class PrivateS3Handler(S3SharingHandler):
    bucket = settings.S3_PRIVATE_BUCKET
    sharing_types = {
        'split': [
            [label] for label in ALL_SHARING_LABELS
        ],
        'combined': [
            ALL_SHARING_LABELS[:ALL_SHARING_LABELS.index(label) + 1]
            for label in ALL_SHARING_LABELS
        ],
    }


class PrivateS3UserHandler(S3UserHandler):
    bucket = settings.S3_PRIVATE_BUCKET


class PublicS3Handler(S3FieldFilteredHandler):
    bucket = settings.S3_PUBLIC_BUCKET
    allowed_fields = ReadingListSerializer.Meta.fields
    sharing_types = {
        'combined': [[readings_choices.SHARING_PUBLIC]],
    }


class DynamoDBHandler(DataHandler):
    durations = settings.STATISTICS_DURATIONS
    bucket = settings.S3_PRIVATE_BUCKET

    @cached_property
    def conn(self):
        return get_conn()

    @cached_property
    def table(self):
        return self.conn.get_table(settings.DYNAMODB_TABLE)

    def process_data(self, data):
        geo_sorted = defaultdict(list)

        for data_point in data:
            for geo_key_length in range(1, 6):
                geo_key = geohash.encode(
                    data_point['latitude'],
                    data_point['longitude'],
                    precision=geo_key_length,
                )
                geo_sorted[geo_key].append(data_point)

        statistics = {}

        for geo_key, data_points in geo_sorted.items():
            readings = [data_point['reading'] for data_point in data_points]
            unique_users = len(
                set([data_point['user_id'] for data_point in data_points]))

            statistics[geo_key] = {
                'min': min(readings),
                'max': max(readings),
                'mean': mean(readings),
                'median': median(readings),
                'std_dev': std_dev(readings),
                'samples': len(readings),
                'users': unique_users,
            }

        return statistics

    def write_data(self, duration, block, data):
        put_items = [
            self.table.new_item(
                hash_key='%s-%s' % (duration, geo_key),
                range_key=int(block),
                attrs=stats,
            ) for geo_key, stats in data.items()]

        for batch_items in group_by(put_items, 25):
            write_items(self.conn, self.table, batch_items)


class BlockSorter(BaseTask):

    def write_to_redis(self, duration, block, reading):
        block_key = get_block_key(duration, block)
        pickled_reading = pickle.dumps(reading)
        REDIS.lpush(block_key, pickled_reading)

    def handle(self, reading):
        reading_date = reading['daterecorded']

        for duration, duration_time in settings.ALL_DURATIONS:
            reading_date_offset = reading_date % duration_time
            block = reading_date - reading_date_offset

            self.write_to_redis(duration, block, reading)


class BlockHandler(BaseTask):
    handlers = (
        PrivateS3Handler,
        PublicS3Handler,
        DynamoDBHandler,
    )
    block_expire = 60 * 60

    def handle(self):
        handled_keys = []
        for key in REDIS.keys():
            if is_block_key(key):
                self.handle_block(key)
                handled_keys.append(key)

    def handle_block(self, block_key):
        duration, block = unpack_block_key(block_key)
        new_block_key = str(uuid.uuid4())

        REDIS.rename(block_key, new_block_key)
        REDIS.expire(new_block_key, self.block_expire)

        for handler in self.handlers:
            if duration in handler.durations:
                handler().delay(new_block_key, duration, block)
