from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from blog.models import BlogPost


class BlogListView(ListView):
    model = BlogPost
    template_name = 'blog/list.html'
    context_object_name = 'blog_posts'

    def get_queryset(self):
        return super(BlogListView, self).get_queryset().filter(published=True)

blog_list = cache_page(BlogListView.as_view(), settings.CACHE_TIMEOUT)


class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/detail.html'
    context_object_name = 'blog_post'

blog_detail = cache_page(BlogDetailView.as_view(), settings.CACHE_TIMEOUT)
