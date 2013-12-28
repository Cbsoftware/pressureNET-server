from rest_framework import serializers

from customers import choices as customers_choices
from customers.models import Customer
from readings.models import Reading, Condition


class ReadingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reading
        fields = (
            'reading',
            'daterecorded',
            'latitude',
            'longitude',
        )


class ReadingLiveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reading
        fields = (
            'reading',
            'latitude',
            'longitude',
            'altitude',
            'daterecorded',
            'user_id',
            'tzoffset',
            'sharing',
            'provider',
            'client_key',
            'location_accuracy',
            'reading_accuracy',
            'observation_type',
            'observation_unit',
        )

    def get_fields(self):
        fields = super(ReadingLiveSerializer, self).get_fields()

        api_key = self.context['view'].request.GET.get('api_key', '')
        customer = Customer.objects.get(api_key=api_key)  # TODO: Handle DoesNotExist case

        if customer.customer_type == customers_choices.CUSTOMER_PUBLIC:
            del fields['user_id']

        return fields


class ConditionListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Condition
        fields = (
            'latitude',
            'longitude',
            'altitude',
            'daterecorded',
            'tzoffset',
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
