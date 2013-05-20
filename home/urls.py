from django.conf.urls import patterns, url


urlpatterns = patterns('home.views',
    url('^$', 'index', name='home-index'),
    url('^livestream/$', 'livestream', name='home-livestream'),
    url('^about/$', 'about', name='home-about'),
)
