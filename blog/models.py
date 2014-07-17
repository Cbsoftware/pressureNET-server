from django.contrib.auth.models import User
from django.db import models

from froala_editor.fields import FroalaField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from utils.image import GaussianBlurSpec


class BlogPost(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name='blog_posts')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    published = models.BooleanField()
    image = models.ImageField(max_length=255, upload_to='blog/images', blank=True, null=True)
    image_blurred = ImageSpecField(source='image', processors=[GaussianBlurSpec()], format='JPEG')
    image_thumbnail = ImageSpecField(source='image', processors=[ResizeToFill(480, 360)], format='JPEG')
    teaser = FroalaField()
    content = FroalaField()

    class Meta:
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
        ordering = ('-creation_date',)

    def __unicode__(self):
        return self.title
