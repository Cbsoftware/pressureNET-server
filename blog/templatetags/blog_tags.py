from django import template
from django.contrib.auth.models import User


from blog.models import BlogPost


register = template.Library()


@register.assignment_tag
def get_authors():
    return User.objects.filter(blog_posts__isnull=False).distinct()


@register.assignment_tag
def get_recent_blog_posts():
    return BlogPost.objects.all().order_by('-creation_date')[:3]


@register.assignment_tag
def get_author_blog_posts(author, exclude_post):
    return BlogPost.objects.filter(author=author).exclude(id=exclude_post.id)[:3]
