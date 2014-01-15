from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView


index = cache_page(TemplateView.as_view(template_name='home/index.html'), settings.CACHE_TIMEOUT)
about = cache_page(TemplateView.as_view(template_name='home/about.html'), settings.CACHE_TIMEOUT)
map_page = cache_page(TemplateView.as_view(template_name='home/map.html'), settings.CACHE_TIMEOUT)
