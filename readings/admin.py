import datetime

from django.core.cache import cache
from django.contrib import admin
from django.utils import simplejson as json

from readings.models import Reading, ReadingSync, Condition
from utils.time_utils import to_unix


class ReadingAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'latitude', 'longitude', 'reading', 'date', 'sharing')
    list_filter = ('sharing',)

    def has_add_permission(self, *args, **kwargs):
        return False

admin.site.register(Reading, ReadingAdmin)


class ReadingSyncAdmin(admin.ModelAdmin):
    list_display = ('date', 'readings', 'processing_time')

admin.site.register(ReadingSync, ReadingSyncAdmin)


class ConditionAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'latitude', 'longitude', 'general_condition', 'date')

admin.site.register(Condition, ConditionAdmin)
