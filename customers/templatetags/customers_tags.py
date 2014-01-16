from django import template

from customers import choices as customers_choices
from customers.models import CustomerType, CustomerPlan

register = template.Library()


@register.assignment_tag
def get_customer_types():
    return CustomerType.objects.all()


@register.assignment_tag
def get_customer_plans():
    return CustomerPlan.objects.all()
