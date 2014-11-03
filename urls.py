from django.conf import settings
from django.contrib import admin
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^froala_editor/', include('froala_editor.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('customers.urls_api')),
    url(r'^developers/', include('customers.urls_developer')),
    url(r'^blog/', include('blog.urls')),
    url(r'^', include('readings.urls')),
    url(r'^', include('home.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
