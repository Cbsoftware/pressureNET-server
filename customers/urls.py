from django.conf.urls import patterns, url


urlpatterns = patterns('customers.views',
    url('^$', 'landing', name='customers-landing'),
    url('^register/$', 'create_customer_view', name='customers-register'),
)
