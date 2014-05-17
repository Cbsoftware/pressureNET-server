from django.contrib.auth.models import User
from django.db import models

from imagekit.models import ImageSpecField

from utils.image import GaussianBlurSpec


class BlogPost(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name='blog_posts')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    teaser = models.TextField()
    image = models.ImageField(max_length=255, upload_to='blog/images', blank=True, null=True)
    image_blurred = ImageSpecField(source='image', processors=[GaussianBlurSpec()], format='PNG')
    content = models.TextField()
    published = models.BooleanField()

    class Meta:
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
        ordering = ('-creation_date',)

    def __unicode__(self):
        return self.title
