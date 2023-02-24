from http import HTTPStatus

from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post, User
from .constants import (
    MAIN_URL_NAME,
    GROUP_URL_NAME,
    PROFILE_URL_NAME,
    POST_DETAIL_URL_NAME,
    POST_CREATE_URL_NAME,
    POST_EDIT_URL_NAME,
    LOGIN_URL_NAME,
    MAIN_TEMPL,
    GROUP_TEMPL,
    PROFILE_TEMPL,
    POST_DETAIL_TEMPL,
    POST_CREATE_TEMPL,
    LOGIN_NEXT_CREATE_URL,
    NONEXIST_URL
)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')

        cls.group = Group.objects.create(
            title='Test Group',
            slug='test-group',
            description='Test',
        )

        cls.post = Post.objects.create(
            text='Test text',
            author=cls.user,
        )
        cls.MAIN_URL = reverse(MAIN_URL_NAME)
        cls.GROUP_URL = reverse(
            GROUP_URL_NAME,
            kwargs={'slug': cls.group.slug}
        )
        cls.PROFILE_URL = reverse(
            PROFILE_URL_NAME,
            kwargs={'username': cls.post.author}
        )
        cls.POST_DETAIL_URL = reverse(
            POST_DETAIL_URL_NAME,
            kwargs={'post_id': cls.post.pk}
        )
        cls.POST_CREATE_URL = reverse(POST_CREATE_URL_NAME)
        cls.POST_EDIT_URL = reverse(
            POST_EDIT_URL_NAME,
            kwargs={'post_id': cls.post.pk}
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_exist_at_desired_location(self):
        """Страницы доступны соответствующему типу пользователя."""
        pages = (
            (self.MAIN_URL, self.guest_client, HTTPStatus.OK),
            (self.GROUP_URL, self.guest_client, HTTPStatus.OK),
            (self.PROFILE_URL, self.guest_client, HTTPStatus.OK),
            (self.POST_DETAIL_URL, self.guest_client, HTTPStatus.OK),
            (NONEXIST_URL, self.guest_client, HTTPStatus.NOT_FOUND),
            (self.POST_CREATE_URL, self.authorized_client, HTTPStatus.OK)
        )
        for url, client, status_code in pages:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_edit_post_url_exists_at_desired_location(self):
        """Страница редактирования поста доступна только
        автору поста."""
        response = self.authorized_client.get(
            self.POST_EDIT_URL,
            author=self.user
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_edit_urls_redirect_anonymous_on_admin_login(self):
        """Страницы создания и редактирования поста перенаправят анонимного
        пользователя на страницу авторизации."""
        pages = (
            (self.POST_CREATE_URL, LOGIN_NEXT_CREATE_URL),
            (self.POST_EDIT_URL,
                reverse(LOGIN_URL_NAME) + '?next=' + self.POST_EDIT_URL)
        )
        for page, url in pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page, follow=True)
                self.assertRedirects(response, url)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_urls = {
            self.MAIN_URL: MAIN_TEMPL,
            self.GROUP_URL: GROUP_TEMPL,
            self.PROFILE_URL: PROFILE_TEMPL,
            self.POST_DETAIL_URL: POST_DETAIL_TEMPL,
            self.POST_CREATE_URL: POST_CREATE_TEMPL,
            self.POST_EDIT_URL: POST_CREATE_TEMPL
        }
        for url_name, template in templates_urls.items():
            with self.subTest(url_name=url_name):
                response = self.authorized_client.get(url_name)
                self.assertTemplateUsed(response, template)
