from django.core.urlresolvers import reverse
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView 
from django.views.generic.edit import CreateView

from customers.forms import CustomerForm
from customers.models import Customer


landing_api = cache_page(TemplateView.as_view(template_name='customers/landing_api.html'), settings.CACHE_TIMEOUT)
landing_developer = cache_page(TemplateView.as_view(template_name='customers/landing_developer.html'), settings.CACHE_TIMEOUT)


class CreateCustomerView(CreateView):
    model = Customer
    form_class = CustomerForm


class CreateAPICustomerView(CreateCustomerView):
    template_name = 'customers/register_api.html'

    def get_success_url(self):
        return '{url}?success=1'.format(url=reverse('customers-landing-api'))

create_api_customer_view = CreateAPICustomerView.as_view()


class CreateDeveloperCustomerView(CreateCustomerView):
    template_name = 'customers/register_developer.html'

    def get_success_url(self):
        return '{url}?success=1'.format(url=reverse('customers-landing-developer'))

create_developer_customer_view = CreateDeveloperCustomerView.as_view()
