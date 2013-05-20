from django.test import TestCase
from django.core.urlresolvers import reverse

from readings import choices as readings_choices
from readings.models import Reading, Condition


class CreateReadingTests(TestCase):

    def get_post_data(self):
        return {
            'user_id': 'abc',
            'latitude': 1.0,
            'longitude': 1.0,
            'altitude': 1.0,
            'reading': 1.0,
            'reading_accuracy': 1.0,
            'provider': 'abc',
            'observation_type': 'abc',
            'observation_unit': 'abc',
            'sharing': readings_choices.SHARING_PUBLIC,
            'daterecorded': 123,
            'tzoffset': 123,
            'location_accuracy': 1.0,
            'client_key': 'abc',
        }

    def test_create_reading_inserts_into_db(self):
        post_data = self.get_post_data()
        response = self.client.post(reverse('readings-create-reading'), post_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reading.objects.count(), 1)


class CreateConditionTests(TestCase):

    def get_post_data(self):
        return {
            'user_id': 'abc',
            'latitude': 1.0,
            'longitude': 1.0,
            'altitude': 1.0,
            'daterecorded': 123,
            'tzoffset': 123,
            'accuracy': 1.0,
            'provider': 'abc',
            'sharing': 'abc',
            'client_key': 'abc',
            'general_condition': 'abc',
            'windy': 'abc',
            'fog_thickness': 'abc',
            'precipitation_type': 'abc',
            'precipitation_amount': 1.0,
            'precipitation_unit': 'abc',
            'thunderstorm_intensity': 'abc',
            'user_comment': 'abc',
        }

    def test_create_reading_inserts_into_db(self):
        post_data = self.get_post_data()
        response = self.client.post(reverse('readings-create-condition'), post_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Condition.objects.count(), 1)
