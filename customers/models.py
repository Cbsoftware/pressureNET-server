from django.db import models

from customers import choices as customer_choices


class Customer(models.Model):
    """Customer data"""
    company_name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    contact_mail = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=25, blank=True, null=True)
    contact_address = models.CharField(max_length=255, blank=True, null=True)
    api_key = models.CharField(max_length=255)
    customer_type = models.CharField(max_length=20, choices=customer_choices.CUSTOMER_TYPES)
    payment_status = models.CharField(max_length=20, blank=True, null=True)
    payment_confirmation = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'customer'
        verbose_name_plural = 'customers'
        unique_together = ('company_name', 'contact_name', 'contact_mail')

    def __unicode__(self):
        return self.company_name


class CustomerCallLog(models.Model):
    """Log data for each customer API call"""
    call_type = models.CharField(max_length=255, choices=customer_choices.CALL_TYPES, default=customer_choices.CALL_READINGS)
    customer = models.ForeignKey(Customer)
    timestamp = models.DateTimeField(auto_now_add=True)
    min_latitude = models.FloatField()
    max_latitude = models.FloatField()
    min_longitude = models.FloatField()
    max_longitude = models.FloatField()
    global_data = models.BooleanField()
    since_last_call = models.BooleanField()
    start_time = models.BigIntegerField()
    end_time = models.BigIntegerField()
    results_limit = models.IntegerField()
    data_format = models.CharField(max_length=10)
    use_utc = models.BooleanField()
    processing_time = models.FloatField()
    results_returned = models.IntegerField()

    class Meta:
        verbose_name = 'Customer Call Log'
        verbose_name_plural = 'Customer Call Logs'

    def __unicode__(self):
        return '%s: %s' % (self.customer, self.timestamp)
