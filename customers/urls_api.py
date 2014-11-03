from django.conf.urls import patterns, url


urlpatterns = patterns('customers.views',
    url('^$', 'landing_api', name='customers-api-landing'),
    url('^register/$', 'create_api_customer_view', name='customers-api-register'),
)
