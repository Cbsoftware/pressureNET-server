import datetime

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView
from django.utils import simplejson as json

from customers.models import Customer, CustomerCallLog
from readings.models import Reading, ReadingSync, Condition
from utils.time_utils import to_unix


index = cache_page(TemplateView.as_view(template_name='home/index.html'), settings.CACHE_TIMEOUT)
about = cache_page(TemplateView.as_view(template_name='home/about.html'), settings.CACHE_TIMEOUT)


class DashboardView(TemplateView):
    template_name = 'home/dashboard.html'

    def get_counts(self, model, date_field, unix_time):
        now = datetime.datetime.now()
        current_date = datetime.datetime(now.year, now.month, now.day, now.hour)

        count_per_hour = []

        for num_hours in range(1, 336):
            start_date = current_date - datetime.timedelta(hours=num_hours)
            end_date = current_date - datetime.timedelta(hours=(num_hours - 1))

            if unix_time:
                start_date = to_unix(start_date)
                end_date = to_unix(end_date)

            filters = {
                '%s__gte' % date_field: start_date,
                '%s__lte' % date_field: end_date,
            }

            count_per_hour.append([
                end_date if unix_time else to_unix(end_date),
                model.objects.all().filter(**filters).count(),
            ])

        return {
            'title': '%s per Hour' % model._meta.verbose_name_plural.capitalize(),
            'id': '_'.join(model._meta.verbose_name_plural.split(' ')),
            'data': count_per_hour,
        }

    def get_context_data(self, **kwargs):
        graphs = [
            (Reading, 'daterecorded', True),
            (ReadingSync, 'date', False),
            (Condition, 'daterecorded', True),
            (Customer, 'creation_date', False),
            (CustomerCallLog, 'timestamp', False),
        ]

        graph_data = [self.get_counts(model, date_field, unix_time) for (model, date_field, unix_time) in graphs]

        context = {
            'graphs': json.dumps(graph_data),
        }

        return context

dashboard = user_passes_test(
    lambda user: user.is_superuser,
    '/admin/login/',
)(
    cache_page(
        DashboardView.as_view(),
        60 * 60,
    )
)
