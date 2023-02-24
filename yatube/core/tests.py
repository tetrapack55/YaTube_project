from http import HTTPStatus

from django.test import TestCase


NONEXIST_URL = '/nonexist/'
TEMPL_404 = 'core/404.html'


class ViewTestClass(TestCase):
    def test_error_page(self):
        """Проверка доступности  кастомной страницы 404."""
        response = self.client.get(NONEXIST_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_error_page_template(self):
        """Проверка  шаблона кастомной страницы 404."""
        response = self.client.get(NONEXIST_URL)
        self.assertTemplateUsed(response, TEMPL_404)
