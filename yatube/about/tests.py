from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_exist_at_desired_location(self):
        """Проверка доступности адресов /author/ и /tech/."""
        urls = ('about:author', 'about:tech')
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(reverse(url))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_urls_use_correct_templates(self):
        """Проверка шаблонов для адресов /author/ и /tech/."""
        template_url_name = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html'
        }
        for url, template in template_url_name.items():
            with self.subTest(url=url):
                response = self.guest_client.get(reverse(url))
                self.assertTemplateUsed(response, template)
