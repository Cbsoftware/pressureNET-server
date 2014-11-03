from django.conf.urls import patterns, url


urlpatterns = patterns('customers.views',
    url('^$', 'landing_developer', name='customers-developer-landing'),
    url('^register/$', 'create_developer_customer_view', name='customers-developer-register'),
)
