from django import template

from customers import choices as customers_choices
from customers.models import CustomerPlan

register = template.Library()


@register.assignment_tag
def get_customer_types():
    return customers_choices.CUSTOMER_FORM_TYPES 


@register.assignment_tag
def get_customer_plans():
    return CustomerPlan.objects.all()
