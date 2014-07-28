import datetime
import time
import urllib2

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotAllowed
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView
from django.utils import simplejson as json

from rest_framework.generics import ListAPIView
from rest_framework.throttling import UserRateThrottle

from customers import choices as customer_choices
from customers.models import Customer, CustomerCallLog

from readings import choices as readings_choices
from readings.forms import ReadingForm, ConditionForm
from readings.filters import ReadingListFilter, ConditionListFilter
from readings.serializers import ReadingListSerializer, ReadingLiveSerializer, ConditionListSerializer
from readings.models import Reading, ReadingSync, Condition, ConditionFilter

from utils.time_utils import to_unix
from utils.loggly import loggly, Logger
from utils.dynamodb import get_item
from utils.geohash import bounding_box_hash


def add_from_pressurenet(request):
    """
    Data is incoming from pressureNET.
    Authenticate and add it to the database.
    """
    start = time.time()
    # get <-> post with urlencode
    result = urllib2.urlopen('http://ec2-174-129-98-143.compute-1.amazonaws.com:8080/BarometerNetworkServer-3.1/BarometerServlet?pndv=buffer')
    content = result.read()
    readings_list = content.split(';')
    count = 0
    for reading in readings_list:
        raw_location_accuracy = 0
        raw_reading_accuracy = 0
        reading_data = reading.split('|')
        if reading_data[0] == '':
            continue
        raw_latitude = float(reading_data[0])
        raw_longitude = float(reading_data[1])
        raw_reading = float(reading_data[2])
        raw_daterecorded = int(float(reading_data[3]))
        raw_tzoffset = int(float(reading_data[4]))
        raw_user_id = reading_data[5]
        raw_sharing = reading_data[6]
        raw_client_key = reading_data[7]
        try:
            raw_location_accuracy = reading_data[8]
            raw_reading_accuracy = reading_data[9]
        except:
            pass
        reading_form = ReadingForm(dict(
            latitude=raw_latitude,
            longitude=raw_longitude,
            reading=raw_reading,
            daterecorded=raw_daterecorded,
            tzoffset=raw_tzoffset,
            user_id=raw_user_id,
            sharing=raw_sharing,
            client_key=raw_client_key,
            location_accuracy=raw_location_accuracy,
            reading_accuracy=raw_reading_accuracy,
            altitude=0.0,
            observation_unit='mbar',
            observation_type='pressure',
            provider='network',
        ))

        if reading_form.is_valid():
            reading_form.save()
        else:
            loggly(
                view='add_reading_from_pressurenet',
                event='invalid form',
                errors=reading_form._errors,
            )

        count += 1

    processing_time = time.time() - start
    ReadingSync.objects.create(readings=count, processing_time=processing_time)
    loggly(
        view='add_reading_from_pressurenet',
        event='save',
        count=count,
    )
    return HttpResponse('okay go, count ' + str(count))


class FilteredListAPIView(ListAPIView):

    def get_queryset(self):
        serializer = self.get_serializer_class()
        queryset = super(FilteredListAPIView, self).get_queryset()

        if hasattr(serializer.Meta, 'fields'):
            fields = serializer.Meta.fields
            queryset = queryset.only(*fields)

        return queryset


class ReadingListView(FilteredListAPIView):
    model = Reading
    serializer_class = ReadingListSerializer
    filter_class = ReadingListFilter

reading_list = cache_page(ReadingListView.as_view(), settings.CACHE_TIMEOUT)

def reading_stats(request):
    try:
        duration_label = request.GET['log_duration']
        start_time = int(request.GET['start_time'])
        end_time = int(request.GET['end_time'])
        min_lat = float(request.GET['min_latitude'])
        max_lat = float(request.GET['max_latitude'])
        min_lon = float(request.GET['min_longitude'])
        max_lon = float(request.GET['max_longitude'])

        geohash = bounding_box_hash(min_lat, min_lon, max_lat, max_lon)

        hash_key = '%s-%s' % (duration_label, geohash)

        stats = get_item(hash_key, start_time, end_time)
    except:
        stats = []

    return HttpResponse(json.dumps(stats), mimetype='application/json')


class ConditionListView(FilteredListAPIView):
    model = Condition
    serializer_class = ConditionListSerializer
    filter_class = ConditionListFilter

    def get_queryset(self, *args, **kwargs):
        queryset = super(ConditionListView, self).get_queryset(*args, **kwargs)

        filter_user_ids = ConditionFilter.objects.all().values_list('user_id', flat=True)
        return queryset.exclude(user_id__in=filter_user_ids)

condition_list = cache_page(ConditionListView.as_view(), settings.CACHE_TIMEOUT)


class APIKeyViewMixin(object):

    def get(self, *args, **kwargs):
        api_key = self.request.GET.get('api_key', '')

        if not Customer.objects.filter(api_key=api_key, api_key_enabled=True).exists():
            return HttpResponseNotAllowed('An active API Key is required')

        return super(APIKeyViewMixin, self).get(*args, **kwargs)


class LoggedLocationListView(FilteredListAPIView):
    """Handle requests for livestreaming"""

    def unpack_parameters(self):
        return {
            'global_data': self.request.GET.get('global', False) == 'true',
            'since_last_call': 'since_last_call' in self.request.GET,
            'min_latitude': self.request.GET.get('min_lat', -180),
            'max_latitude': self.request.GET.get('max_lat', 180),
            'min_longitude': self.request.GET.get('min_lon', -180),
            'max_longitude': self.request.GET.get('max_lon', 180),
            'start_time': self.request.GET.get('start_time', (time.time() - 3600 * 24) * 1000),
            'end_time': self.request.GET.get('end_time', time.time() * 1000),
            'results_limit': self.request.GET.get('limit', 1000000),
            'api_key': self.request.GET.get('api_key', ''),
            'data_format': self.request.GET.get('format', 'json'),
        }

    def get(self, *args, **kwargs):
        start = time.time()

        response = super(LoggedLocationListView, self).get(*args, **kwargs)

        parameters = self.unpack_parameters()
        call_log = CustomerCallLog(call_type=self.call_type)
        call_log.customer = Customer.objects.get(api_key=parameters['api_key'])  # TODO: Handle DoesNotExist case
        call_log.results_returned = len(response.data)
        call_log.query = ''
        call_log.path = '%s?%s' % (self.request.path, self.request.META['QUERY_STRING'])
        call_log.data_format = parameters['data_format']
        call_log.min_latitude = parameters['min_latitude']
        call_log.max_latitude = parameters['max_latitude']
        call_log.min_longitude = parameters['min_longitude']
        call_log.max_longitude = parameters['max_longitude']
        call_log.global_data = parameters['global_data']
        call_log.since_last_call = parameters['since_last_call']
        call_log.start_time = parameters['start_time']
        call_log.end_time = parameters['end_time']
        call_log.results_limit = parameters['results_limit']
        call_log.use_utc = ''
        call_log.processing_time = time.time() - start
        call_log.ip_address = self.request.META['REMOTE_ADDR']
        call_log.save()

        return response

    def get_queryset(self):
        parameters = self.unpack_parameters()

        customer = Customer.objects.get(api_key=parameters['api_key'])  # TODO: Handle DoesNotExist case
        queryset = super(LoggedLocationListView, self).get_queryset()

        if not parameters['global_data']:
            queryset = queryset.filter(
                latitude__gte=parameters['min_latitude'],
                latitude__lte=parameters['max_latitude'],
                longitude__gte=parameters['min_longitude'],
                longitude__lte=parameters['max_longitude'],
            )

        call_logs = CustomerCallLog.objects.filter(customer=customer)
        if parameters['since_last_call'] and call_logs.exists():
            call_log = call_logs.order_by('-timestamp')[:1].get()
            queryset = queryset.filter(
                daterecorded__gte=to_unix(call_log.timestamp),
            )
        else:
            queryset = queryset.filter(
                daterecorded__gte=parameters['start_time'],
                daterecorded__lte=parameters['end_time'],
            )

        if customer.customer_type == customer_choices.CUSTOMER_PUBLIC:
            queryset = queryset.filter(sharing=readings_choices.SHARING_PUBLIC)

        elif customer.customer_type == customer_choices.CUSTOMER_RESEARCHER:
            queryset = queryset.filter(sharing__in=[
                readings_choices.SHARING_PUBLIC,
                readings_choices.SHARING_RESEARCHERS_FORECASTERS,
                readings_choices.SHARING_RESEARCHERS,
            ])

        elif customer.customer_type == customer_choices.CUSTOMER_FORECASTER:
            queryset = queryset.filter(sharing__in=[
                readings_choices.SHARING_PUBLIC,
                readings_choices.SHARING_RESEARCHERS_FORECASTERS,
            ])

        return queryset[:parameters['results_limit']]


class ReadingLiveView(APIKeyViewMixin, LoggedLocationListView):
    """Handle requests for livestreaming"""
    call_type = customer_choices.CALL_READINGS
    model = Reading
    serializer_class = ReadingLiveSerializer
    throttle_classes = (UserRateThrottle,)

reading_live = ReadingLiveView.as_view()


class JSONCreateView(Logger, CreateView):

    def log_response(self, response):
        self.log(
            response=response,
        )

    def form_valid(self, form):
        form.save()

        response = {
            'success': True,
            'client_key': form.cleaned_data.get('client_key', ''),
            'errors': '',
        }

        self.log_response(response)

        return HttpResponse(
            json.dumps(response),
            mimetype='application/json'
        )

    def form_invalid(self, form):
        response = {
            'success': False,
            'client_key': form.cleaned_data.get('client_key', ''),
            'errors': form._errors,
        }

        self.log_response(response)

        return HttpResponse(
            json.dumps(response),
            mimetype='application/json'
        )


class CreateReadingView(JSONCreateView):
    model = Reading
    form_class = ReadingForm

create_reading = csrf_exempt(CreateReadingView.as_view())


class CreateConditionView(JSONCreateView):
    model = Condition
    form_class = ConditionForm

create_condition = csrf_exempt(CreateConditionView.as_view())
