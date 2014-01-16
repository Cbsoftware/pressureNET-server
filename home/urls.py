from django.conf.urls import patterns, url


urlpatterns = patterns('home.views',
    url('^$', 'index', name='home-index'),
    url('^about/$', 'about', name='home-about'),
    url('^map/$', 'map_page', name='home-map'),
)
