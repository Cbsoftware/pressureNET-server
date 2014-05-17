from django.conf.urls import patterns, url


urlpatterns = patterns(
    'blog.views',
    url('^$', 'blog_list', name='blog-list'),
    url('^author/(?P<author>[-_\w]+)/$', 'blog_list_author', name='blog-list-author'),
    url(r'^(?P<slug>[-_\w]+)/$', 'blog_detail', name='blog-detail'), 
)
