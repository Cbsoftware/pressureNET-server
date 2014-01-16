from django.db import models

from customers import choices as customer_choices


class CustomerPlan(models.Model):
    """Customer plan"""
    name = models.CharField(max_length=255)
    description = models.TextField()
    global_calls = models.IntegerField(blank=True, null=True)
    region_calls = models.IntegerField(blank=True, null=True)
    regions = models.IntegerField(blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = 'Customer Plan'
        verbose_name_plural = 'Customer Plans'

    def __unicode__(self):
        return self.name


class CustomerType(models.Model):
    """Customer Type"""
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        verbose_name = 'Customer Type'
        verbose_name_plural = 'Customer Types'

    def __unicode__(self):
        return self.name


class Customer(models.Model):
    """Customer data"""
    creation_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    #customer_type = models.CharField(max_length=20, choices=customer_choices.CUSTOMER_TYPES)
    customer_type = models.ForeignKey(CustomerType, blank=True, null=True) 
    customer_plan = models.ForeignKey(CustomerPlan, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    contact_name = models.CharField(max_length=255)
    contact_mail = models.EmailField(max_length=100, unique=True)
    contact_phone = models.CharField(max_length=25, blank=True, null=True)
    contact_address = models.CharField(max_length=255, blank=True, null=True)
    api_key = models.CharField(max_length=255)
    api_key_enabled = models.BooleanField(default=True)
    payment_status = models.CharField(max_length=20, blank=True, null=True)
    payment_confirmation = models.CharField(max_length=255, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __unicode__(self):
        return self.contact_name


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
    path = models.TextField()
    query = models.TextField()
    processing_time = models.FloatField()
    results_returned = models.IntegerField()
    ip_address = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'Customer Call Log'
        verbose_name_plural = 'Customer Call Logs'

    def __unicode__(self):
        return '%s: %s' % (self.customer, self.timestamp)
