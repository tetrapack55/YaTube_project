import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post, User
from posts.utils import POSTS_LIMIT
from .constants import (
    MAIN_URL_NAME,
    GROUP_URL_NAME,
    PROFILE_URL_NAME,
    POST_DETAIL_URL_NAME,
    POST_CREATE_URL_NAME,
    POST_EDIT_URL_NAME,
    MAIN_TEMPL,
    GROUP_TEMPL,
    PROFILE_TEMPL,
    POST_DETAIL_TEMPL,
    POST_CREATE_TEMPL,
    SMALL_GIF,
)


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )

        cls.user = User.objects.create_user(username='TestUser')

        cls.group = Group.objects.create(
            title='Test Group',
            slug='test-group',
            description='Test',
        )

        cls.second_group = Group.objects.create(
            title='Test Group 2',
            slug='test-group-2',
            description='Группа2',
        )

        cls.post = Post.objects.create(
            text='Test text',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse(MAIN_URL_NAME): MAIN_TEMPL,
            reverse(
                GROUP_URL_NAME,
                kwargs={'slug': self.group.slug}
            ): GROUP_TEMPL,
            reverse(
                PROFILE_URL_NAME,
                kwargs={'username': self.post.author}
            ): PROFILE_TEMPL,
            reverse(
                POST_DETAIL_URL_NAME,
                kwargs={'post_id': self.post.pk}
            ): POST_DETAIL_TEMPL,
            reverse(POST_CREATE_URL_NAME): POST_CREATE_TEMPL,
            reverse(
                POST_EDIT_URL_NAME,
                kwargs={'post_id': self.post.pk}
            ): POST_CREATE_TEMPL,
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(MAIN_URL_NAME))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author, self.user)
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.group.title, self.group.title)
        self.assertEqual(first_object.image, self.post.image)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse(GROUP_URL_NAME, kwargs={'slug': 'test-group'})))
        self.assertEqual(response.context.get('group').title, self.group.title)
        self.assertEqual(
            response.context.get('group').description,
            self.group.description
        )
        self.assertEqual(response.context.get('group').slug, self.group.slug)
        self.assertEqual(response.context.get('post').image, self.post.image)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse(PROFILE_URL_NAME, kwargs={'username': self.post.author})))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author, self.user)
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.group.title, self.group.title)
        self.assertEqual(first_object.image, self.post.image)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(POST_DETAIL_URL_NAME, kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(response.context.get('post').author, self.user)
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').group, self.group)
        self.assertEqual(response.context.get('post').image, self.post.image)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(POST_CREATE_URL_NAME))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(POST_EDIT_URL_NAME, kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_added_correctly(self):
        """Пост при создании добавлен только на требуемые страницы"""
        response_index = self.authorized_client.get(
            reverse(MAIN_URL_NAME))
        response_group = self.authorized_client.get(
            reverse(GROUP_URL_NAME,
                    kwargs={'slug': self.group.slug}))
        response_profile = self.authorized_client.get(
            reverse(PROFILE_URL_NAME,
                    kwargs={'username': self.user}))
        response_group2 = self.authorized_client.get(
            reverse(GROUP_URL_NAME,
                    kwargs={'slug': self.second_group.slug}))
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        group2 = response_group2.context['page_obj']
        self.assertIn(self.post, index)
        self.assertIn(self.post, group)
        self.assertIn(self.post, profile)
        self.assertNotIn(self.post, group2)

    def test_cache(self):
        """Проверка работы кэша главной страницы."""
        old_response = self.authorized_client.get(reverse(MAIN_URL_NAME))
        Post.objects.get(pk=self.post.pk).delete()
        cache.clear()
        new_response = self.authorized_client.get(reverse(MAIN_URL_NAME))
        self.assertNotEqual(old_response.content, new_response.content)

    def test_follow_and_unfollow(self):
        """Проверка подписки и отписки на авторов"""
        following_user = User.objects.create(username='FollowingUser')
        follow_count = Follow.objects.count()
        response = self.authorized_client.get(
            reverse('posts:profile_follow', args=(following_user,))
        )
        self.assertRedirects(
            response,
            reverse(PROFILE_URL_NAME, args=(following_user,))
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user, author=following_user
            ).exists()
        )
        response = self.authorized_client.get(
            reverse('posts:profile_unfollow', args=(following_user,))
        )
        self.assertRedirects(
            response,
            reverse(PROFILE_URL_NAME, args=(following_user,))
        )
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_follow_index(self):
        """Проверка формирования ленты постов избранных авторов"""
        following_user = User.objects.create(username='FollowingUser')
        post = Post.objects.create(
            text='Test follow',
            author=following_user,
        )
        Follow.objects.create(user=self.user, author=following_user)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertContains(response, post)
        Follow.objects.filter(user=self.user, author=following_user).delete()
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotContains(response, post)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')

        cls.group = Group.objects.create(
            title='Test Group',
            slug='test-group',
            description='Test',
        )
        cls.POST_TOTAL = 13
        cls.posts = (Post(
            text="Тест паджинатора",
            author=cls.user,
            group=cls.group) for _ in range(cls.POST_TOTAL))
        Post.objects.bulk_create(cls.posts)
        cache.clear()

    def test_page_contains_ten_records(self):
        POSTS_ON_FIRST = POSTS_LIMIT
        POSTS_ON_SECOND = self.POST_TOTAL - POSTS_ON_FIRST
        pages = (
            (1, POSTS_ON_FIRST),
            (2, POSTS_ON_SECOND)
        )
        urls = (
            reverse(MAIN_URL_NAME),
            reverse(PROFILE_URL_NAME, kwargs={'username': self.user}),
            reverse(GROUP_URL_NAME, kwargs={'slug': self.group.slug})
        )
        for url_name in urls:
            for page, posts_quantity in pages:
                with self.subTest(url_name=url_name, page=page):
                    if page == 1:
                        response = self.client.get(url_name)
                    else:
                        response = self.client.get((url_name) + '?page=2')
                    self.assertEqual(
                        len(response.context.get('page_obj').object_list),
                        posts_quantity
                    )
