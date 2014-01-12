from django.conf.urls import patterns, url


urlpatterns = patterns('customers.views',
    url('^developers/$', 'create_customer_view', name='customers-developers'),
)
