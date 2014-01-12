from django.core.urlresolvers import reverse
from django.views.generic.edit import CreateView

from customers.forms import CustomerForm
from customers.models import Customer


class CreateCustomerView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/developers.html'

    def get_success_url(self):
        return '%s?success=1' % (reverse('customers-developers'),)

create_customer_view = CreateCustomerView.as_view()
