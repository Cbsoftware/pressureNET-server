from django.conf import settings
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


class CardTests(TestCase):

    def test_card_page_redirects_to_play_store(self):
        response = self.client.get(reverse('home-card'), follow=False)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['location'], settings.PLAY_STORE_URL)
