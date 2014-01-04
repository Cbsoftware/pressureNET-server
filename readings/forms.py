from django import forms
from django.conf import settings

from readings.models import Reading, Condition

from utils.queue import get_queue, add_to_queue
from utils.loggly import loggly


class LoggedForm(forms.ModelForm):

    def save(self, *args, **kwargs):
        loggly(
            view='create',
            model=self.Meta.model.__name__,
            event='save',
        )
        return super(LoggedForm, self).save(*args, **kwargs)


class ReadingForm(LoggedForm):

    class Meta:
        model = Reading
        fields = (
            'user_id',
            'latitude',
            'longitude',
            'altitude',
            'reading',
            'reading_accuracy',
            'provider',
            'observation_type',
            'observation_unit',
            'sharing',
            'daterecorded',
            'tzoffset',
            'location_accuracy',
            'client_key',
        )

    def save(self, *args, **kwargs):
        # Add data to SQS queue
        queue = get_queue(settings.SQS_QUEUE)
        add_to_queue(queue, self.cleaned_data)

        loggly(
            view='create',
            event='sent to queue',
            model='Reading',
        )

        return super(ReadingForm, self).save(*args, **kwargs)


class ConditionForm(LoggedForm):

    class Meta:
        model = Condition
        fields = (
            'user_id',
            'latitude',
            'longitude',
            'altitude',
            'daterecorded',
            'tzoffset',
            'accuracy',
            'provider',
            'sharing',
            'client_key',
            'general_condition',
            'windy',
            'fog_thickness',
            'cloud_type',
            'precipitation_type',
            'precipitation_amount',
            'precipitation_unit',
            'thunderstorm_intensity',
            'user_comment',
        )
