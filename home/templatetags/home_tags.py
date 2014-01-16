from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def get_playstore_url():
    return settings.PLAY_STORE_URL
