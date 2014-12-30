from django.conf.urls import patterns, url


urlpatterns = patterns('readings.views',
    url('^list/$', 'reading_list', name='readings-list'),
    url('^conditions/list/$', 'condition_list', name='readings-conditions-list'),
    url('^live/$', 'reading_live', name='readings-live'),
    url('^add/$', 'create_reading', name='readings-create-reading'),
    url('^conditions/add/$', 'create_condition', name='readings-create-condition'),
)
