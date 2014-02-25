from django.conf.urls import patterns, url


urlpatterns = patterns(
    'blog.views',
    url('^$', 'blog_list', name='blog-list'),
    url(r'^(?P<slug>[-_\w]+)/$', 'blog_detail', name='blog-detail'), 
)
