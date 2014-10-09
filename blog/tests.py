from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from blog.models import BlogPost

import factory


class UserFactory(factory.Factory):
    FACTORY_FOR = User

    username = factory.Sequence(lambda n: 'person{0}@example.com'.format(n))
    first_name = factory.Sequence(lambda n: 'person{0}'.format(n))


class BlogPostFactory(factory.Factory):
    FACTORY_FOR = BlogPost

    author = factory.SubFactory(UserFactory)
    title = 'Title'
    slug = 'slug'
    content = 'content'
    teaser = 'teaser'
    published = True
    image = 'image.jpg'


class BlogListTest(TestCase):

    def test_blog_list_page_loads(self):
        response = self.client.get(reverse('blog-list'))
        self.assertEqual(response.status_code, 200)


class BlogDetailTest(TestCase):

    def test_blog_detail_page_loads(self):
        user = UserFactory()
        user.save()

        post = BlogPostFactory(author=user)
        post.save()

        response = self.client.get(reverse('blog-detail', kwargs={'slug': post.slug}))
        self.assertEqual(response.status_code, 200)
