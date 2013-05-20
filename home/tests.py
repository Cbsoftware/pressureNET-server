from django.core.urlresolvers import reverse
from django.test import TestCase


class TemplateTestMixin(object):

    def test_page_renders_with_correct_template_and_200(self):
        response = self.client.get(reverse(self.url_name))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)


class IndexTests(TemplateTestMixin, TestCase):
    url_name = 'home-index'
    template_name = 'home/index.html'


class AboutTests(TemplateTestMixin, TestCase):
    url_name = 'home-about'
    template_name = 'home/about.html'


class LiveStreamTests(TemplateTestMixin, TestCase):
    url_name = 'home-livestream'
    template_name = 'home/livestream.html'
