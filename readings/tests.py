import datetime
import random
import uuid

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import simplejson as json

import factory

from readings import choices as readings_choices
from readings.models import Reading, Condition

from utils.queue import get_queue
from utils.time_utils import to_unix


class DateLocationMeasurementFactory(factory.Factory):
    date = factory.LazyAttribute(
        lambda reading: datetime.datetime.now()
    )
    user_id = factory.LazyAttribute(
        lambda reading: uuid.uuid4().get_hex()
    )
    latitude = factory.LazyAttribute(
        lambda reading: (random.random() * 180) - 90
    )
    longitude = factory.LazyAttribute(
        lambda reading: (random.random() * 360) - 180
    )
    altitude = factory.LazyAttribute(
        lambda reading: random.random() * 300
    )
    daterecorded = factory.LazyAttribute(
        lambda reading: to_unix(datetime.datetime.now())
    )
    tzoffset = factory.LazyAttribute(
        lambda reading: random.randint(0, 100) * 1000
    )
    client_key = 'ca.cumulonimbus.barometernetwork'
    sharing = readings_choices.SHARING_PUBLIC
    provider = 'gps'


class ReadingFactory(DateLocationMeasurementFactory):
    FACTORY_FOR = Reading

    reading = factory.LazyAttribute(
        lambda reading: (random.random() * 300) + 800
    )
    reading_accuracy = 1.0
    observation_type = 'pressure'
    observation_unit = 'mbars'
    location_accuracy = 0.0


class ConditionFactory(DateLocationMeasurementFactory):
    FACTORY_FOR = Condition

    accuracy = 1.0
    general_condition = 'condition'
    windy = 'abc'
    cloud_type = 'abc'
    fog_thickness = 'abc'
    precipitation_type = 'abc'
    precipitation_amount = 1.0
    precipitation_unit = 'abc'
    thunderstorm_intensity = 'abc'
    user_comment = 'abc'


class DateLocationFilteredListTests(object):

    def test_list_view_returns_readings_above_min_lat(self):
        now = to_unix(datetime.datetime.now())

        self.factory(latitude=1.0, longitude=1.0, daterecorded=now).save()
        self.factory(latitude=2.0, longitude=1.0, daterecorded=now).save()

        response = self.client.get(reverse(self.url_name), {
            'min_latitude': 2.0,
            'max_latitude': 2.0,
            'min_longitude': 1.0,
            'max_longitude': 1.0,
            'start_time': now,
            'end_time': now,
            'limit': 1000,
        })

        data = json.loads(response.content)

        self.assertEquals(len(data), 1)

    def test_list_view_returns_readings_below_max_lat(self):
        now = to_unix(datetime.datetime.now())

        self.factory(latitude=1.0, longitude=1.0, daterecorded=now).save()
        self.factory(latitude=2.0, longitude=1.0, daterecorded=now).save()

        response = self.client.get(reverse(self.url_name), {
            'min_latitude': 1.0,
            'max_latitude': 1.0,
            'min_longitude': 1.0,
            'max_longitude': 1.0,
            'start_time': now,
            'end_time': now,
            'limit': 1000,
        })

        data = json.loads(response.content)

        self.assertEquals(len(data), 1)

    def test_list_view_returns_readings_above_min_lon(self):
        now = to_unix(datetime.datetime.now())

        self.factory(latitude=1.0, longitude=1.0, daterecorded=now).save()
        self.factory(latitude=1.0, longitude=2.0, daterecorded=now).save()

        response = self.client.get(reverse(self.url_name), {
            'min_latitude': 1.0,
            'max_latitude': 1.0,
            'min_longitude': 2.0,
            'max_longitude': 2.0,
            'start_time': now,
            'end_time': now,
            'limit': 1000,
        })

        data = json.loads(response.content)

        self.assertEquals(len(data), 1)

    def test_list_view_returns_readings_below_max_lon(self):
        now = to_unix(datetime.datetime.now())

        self.factory(latitude=1.0, longitude=1.0, daterecorded=now).save()
        self.factory(latitude=1.0, longitude=2.0, daterecorded=now).save()

        response = self.client.get(reverse(self.url_name), {
            'min_latitude': 1.0,
            'max_latitude': 1.0,
            'min_longitude': 1.0,
            'max_longitude': 1.0,
            'start_time': now,
            'end_time': now,
            'limit': 1000,
        })

        data = json.loads(response.content)

        self.assertEquals(len(data), 1)

    def test_list_view_returns_readings_after_starttime(self):
        now = to_unix(datetime.datetime.now())

        self.factory(latitude=1.0, longitude=1.0, daterecorded=now).save()
        self.factory(latitude=1.0, longitude=1.0, daterecorded=now + 1).save()

        response = self.client.get(reverse(self.url_name), {
            'min_latitude': 1.0,
            'max_latitude': 1.0,
            'min_longitude': 1.0,
            'max_longitude': 1.0,
            'start_time': now + 1,
            'end_time': now + 1,
            'limit': 1000,
        })

        data = json.loads(response.content)

        self.assertEquals(len(data), 1)

    def test_list_view_returns_readings_before_endtime(self):
        now = to_unix(datetime.datetime.now())

        self.factory(latitude=1.0, longitude=1.0, daterecorded=now).save()
        self.factory(latitude=1.0, longitude=1.0, daterecorded=now + 1).save()

        response = self.client.get(reverse(self.url_name), {
            'min_latitude': 1.0,
            'max_latitude': 1.0,
            'min_longitude': 1.0,
            'max_longitude': 1.0,
            'start_time': now,
            'end_time': now,
            'limit': 1000,
        })

        data = json.loads(response.content)

        self.assertEquals(len(data), 1)

    def test_list_view_returns_at_most_limit_readings(self):
        now = to_unix(datetime.datetime.now())

        for i in range(3):
            self.factory(latitude=1.0, longitude=1.0, daterecorded=now).save()

        response = self.client.get(reverse(self.url_name), {
            'min_latitude': 1.0,
            'max_latitude': 1.0,
            'min_longitude': 1.0,
            'max_longitude': 1.0,
            'start_time': now,
            'end_time': now,
            'limit': 1000,
        })

        data = json.loads(response.content)

        self.assertEquals(len(data), 3)

        response = self.client.get(reverse(self.url_name), {
            'min_latitude': 1.0,
            'max_latitude': 1.0,
            'min_longitude': 1.0,
            'max_longitude': 1.0,
            'start_time': now,
            'end_time': now,
            'limit': 1,
        })

        data = json.loads(response.content)

        self.assertEquals(len(data), 1)

    @override_settings(MAX_CALL_LENGTH=10)
    def test_list_view_without_limit_defaults_to_global_limit(self):
        now = to_unix(datetime.datetime.now())

        for i in range(11):
            self.factory(latitude=1.0, longitude=1.0, daterecorded=now).save()

        response = self.client.get(reverse(self.url_name), {
            'min_latitude': 1.0,
            'max_latitude': 1.0,
            'min_longitude': 1.0,
            'max_longitude': 1.0,
            'start_time': now,
            'end_time': now,
            'limit': 3,
        })

        data = json.loads(response.content)

        self.assertEquals(len(data), 3)

        response = self.client.get(reverse(self.url_name), {
            'min_latitude': 1.0,
            'max_latitude': 1.0,
            'min_longitude': 1.0,
            'max_longitude': 1.0,
            'start_time': now,
            'end_time': now,
        })

        data = json.loads(response.content)

        self.assertEquals(len(data), 10)

    def test_list_view_returns_readings_within_query_parameters(self):
        now = to_unix(datetime.datetime.now())

        for lat in range(5):
            for lon in range(5):
                for days_delta in range(-2, 3):
                    daterecorded = now + days_delta
                    self.factory(
                        latitude=lat,
                        longitude=lon,
                        daterecorded=daterecorded,
                    ).save()

        response = self.client.get(reverse(self.url_name), {
            'min_latitude': 2.0,
            'max_latitude': 4.0,
            'min_longitude': 2.0,
            'max_longitude': 4.0,
            'start_time': now - 1,
            'end_time': now + 1,
            'limit': 1000,
        })

        data = json.loads(response.content)

        self.assertEquals(len(data), 27)


class ReadingsListTests(DateLocationFilteredListTests, TestCase):
    url_name = 'readings-list'
    factory = ReadingFactory


class ConditionsListTests(DateLocationFilteredListTests, TestCase):
    url_name = 'readings-conditions-list'
    factory = ConditionFactory


class ReadingLiveTests(TestCase):
    pass


class CreateReadingTests(TestCase):

    def __init__(self, *args, **kwargs):
        self.queue = get_queue(settings.SQS_QUEUE)
        return super(CreateReadingTests, self).__init__(*args, **kwargs)

    def clear_queue(self):
        if 'live' in settings.SQS_QUEUE:
            raise Exception('Attempting to test against live queue')

        self.queue.clear()

    def setUp(self):
        self.clear_queue()

    def tearDown(self):
        self.clear_queue()

    def get_post_data(self):
        return ReadingFactory.attributes()

    def test_create_reading_inserts_into_db(self):
        post_data = self.get_post_data()
        response = self.client.post(reverse('readings-create-reading'), post_data)

        response_json = json.loads(response.content)
        self.assertTrue(response_json['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reading.objects.count(), 1)

        queued_messages = self.queue.get_messages(num_messages=10)
        self.assertEqual(len(queued_messages), 1)


class CreateConditionTests(TestCase):

    def get_post_data(self):
        return ConditionFactory.attributes()

    def test_create_reading_inserts_into_db(self):
        post_data = self.get_post_data()
        response = self.client.post(reverse('readings-create-condition'), post_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Condition.objects.count(), 1)
