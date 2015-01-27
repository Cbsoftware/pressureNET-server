import copy

from django import forms
from django.conf import settings

from readings.models import Reading, Condition
from tasks.aggregator import BlockSorter
from utils.queue import get_queue, add_to_queue


class ReadingForm(forms.ModelForm):
    is_charging = forms.CharField(required=False) 
    model_type  = forms.CharField(required=False)
    version_number = forms.CharField(required=False)
    package_name = forms.CharField(required=False)

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
            'is_charging', 
            'model_type',
            'version_number',
            'package_name',
        )

    def save(self, *args, **kwargs):
        reading_data = copy.copy(self.cleaned_data)
        del reading_data['client_key']
        BlockSorter().delay(reading_data)
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
