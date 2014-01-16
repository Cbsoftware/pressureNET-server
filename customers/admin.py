from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from customers.models import CustomerPlan, CustomerType, Customer, CustomerCallLog


class CustomerPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'global_calls', 'region_calls', 'regions', 'price')

admin.site.register(CustomerPlan, CustomerPlanAdmin)


class CustomerTypeAdmin(admin.ModelAdmin):
    pass

admin.site.register(CustomerType, CustomerTypeAdmin)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('contact_name', 'company_name', 'contact_mail', 'customer_type', 'customer_calls', 'creation_date', 'api_key_enabled')
    list_filter = ('customer_type', 'api_key_enabled')
    readonly_fields = ('creation_date', 'api_key')
    fieldsets = (
        ('Administration', {
            'fields': (
                'creation_date',
                'api_key',
                'api_key_enabled',
            ),
        }),
        ('Plan', {
            'fields': (
                'customer_type',
                'customer_plan',
            ),
        }),
        ('Customer', {
            'fields': (
                'contact_name',
                'contact_mail',
                'company_name',
                'contact_phone',
                'contact_address',
                'comments',
            ),
        }),
    )

    def customer_calls(self, instance):
        return mark_safe('<a href="%s?customer__id__exact=%s">%s</a>' % (
            reverse('admin:customers_customercalllog_changelist'),
            instance.id,
            instance.customercalllog_set.count(),
        ))

admin.site.register(Customer, CustomerAdmin)


class CustomerCallLogAdmin(admin.ModelAdmin):
    list_display = ('customer', 'results_returned', 'processing_time', 'timestamp', 'ip_address', 'call_type')
    list_filter = ('customer', 'call_type',)

admin.site.register(CustomerCallLog, CustomerCallLogAdmin)
