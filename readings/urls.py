from django.conf.urls import patterns, url


urlpatterns = patterns('readings.views',
    url('^list/$', 'reading_list', name='readings-list'),
    url('^live/$', 'reading_live', name='readings-live'),
    url('^add/$', 'create_reading', name='readings-create-reading'),
    url('^addfrompressurenet/$', 'add_from_pressurenet', name='readings-addfrompressurenet'),
    url('^conditions/live/$', 'condition_live', name='readings-condition-live'),
    url('^conditions/add/$', 'create_condition', name='readings-create-condition'),
)
