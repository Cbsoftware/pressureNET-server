import datetime
import time
import urllib2

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, Http404, HttpResponseNotAllowed
from django.shortcuts import redirect
from django.utils import simplejson as json
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView

from rest_framework.generics import ListAPIView
from rest_framework.throttling import UserRateThrottle

from customers import choices as customer_choices
from customers.models import Customer, CustomerCallLog

from readings import choices as readings_choices
from readings.filters import ReadingListFilter, ConditionListFilter
from readings.forms import ReadingForm, ConditionForm
from readings.models import Reading, ReadingSync, Condition, ConditionFilter
from readings.serializers import ReadingListSerializer, ReadingLiveSerializer, ConditionListSerializer

from utils.dynamodb import get_item
from utils.geohash import bounding_box_hash
from utils.loggly import loggly, Logger
from utils.s3 import get_file
from utils.time_utils import to_unix


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


def get_s3_file(request):
    response = HttpResponse(status=400)
    file_path = None
    error = None

    start = time.time()

    try:
        api_key = request.GET.get('api_key', None)
        timestamp_block = None

        file_format = request.GET.get('format', 'json')

        timestamp = int(request.GET.get('timestamp', 0)) or int(time.time() * 1000)
        
        if not (api_key and Customer.objects.filter(api_key=api_key, api_key_enabled=True).exists()):
            response = HttpResponseNotAllowed('An active API Key is required')
        else:
            customer = Customer.objects.get(api_key=api_key)

            duration_label, duration_time = settings.ALL_DURATIONS[0]
            timestamp_offset = timestamp % duration_time
            timestamp_block = timestamp - timestamp_offset

            if not customer.customer_type:
                response = HttpResponseNotAllowed('You are not authorized to request this API.  Please contact support.')
            else:
                file_path = 'readings/pressure/combined/{sharing}/{format}/10minute/{timestamp}.{format}'.format(
                    sharing=customer.customer_type.sharing, format=file_format, timestamp=timestamp_block)
                s3_file = get_file(file_path)
                if s3_file:
                    response = redirect(s3_file.generate_url(1000))
                else:
                    response = HttpResponse(status=404)
    except Exception, e:
        error = str(e)

    end = time.time()
    loggly(**{
        'class': 'S3FileView',
        'time': (end - start),
        'api_key': api_key,
        'timestamp': timestamp,
        'timestamp_block': timestamp_block,
        'status': response.status_code,
        's3_file': file_path,
        'error': error,
    })

    return response
