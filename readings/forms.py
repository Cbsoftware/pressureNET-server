from django import forms

from readings.models import Reading, Condition

from utils.queue import add_to_queue


class ReadingForm(forms.ModelForm):

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
        add_to_queue(self.data)
        return super(ReadingForm, self).save(*args, **kwargs)


class ConditionForm(forms.ModelForm):

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
