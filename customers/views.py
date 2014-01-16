from django.core.urlresolvers import reverse
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView 
from django.views.generic.edit import CreateView

from customers.forms import CustomerForm
from customers.models import Customer


landing = cache_page(TemplateView.as_view(template_name='customers/landing.html'), settings.CACHE_TIMEOUT)


class CreateCustomerView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/register.html'

    def get_success_url(self):
        return '%s?success=1' % (reverse('customers-landing'),)

create_customer_view = CreateCustomerView.as_view()
