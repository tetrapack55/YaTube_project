import shutil
import tempfile

from http import HTTPStatus
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post, User
from .constants import (
    PROFILE_URL_NAME,
    POST_CREATE_URL_NAME,
    POST_DETAIL_URL_NAME,
    POST_EDIT_URL_NAME,
    LOGIN_NEXT_CREATE_URL,
    SMALL_GIF,
    ADD_COMMENT_URL_NAME,
)


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')

        cls.group = Group.objects.create(
            title='Test Group',
            slug='test-group',
            description='Test',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_guest_client(self):
        '''Проверка создания поста неавторизованным пользователем'''
        form_data = {'text': 'Test text',
                     'group': self.group.pk}
        response = self.guest_client.post(
            reverse(POST_CREATE_URL_NAME),
            data=form_data,
            follow=True
        )
        self.assertIsNone(Post.objects.first())
        self.assertRedirects(response, LOGIN_NEXT_CREATE_URL)

    def test_create_post_authorized_client(self):
        '''Проверка создания поста авторизованным пользователем'''
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        UPLOADED_DIR = f'posts/{uploaded}'
        form_data = {
            'text': 'Test text',
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse(POST_CREATE_URL_NAME),
            data=form_data,
            follow=True
        )
        post = Post.objects.first()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.pk, form_data['group'])
        self.assertEqual(post.image, UPLOADED_DIR)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(
            response, reverse(PROFILE_URL_NAME, kwargs={'username': self.user})
        )

    def test_post_edit(self):
        '''Проверка редактирования поста'''
        post = Post.objects.create(
            text='Test text',
            author=self.user,
            group=self.group
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Отредактированный текст',
            'group': self.group.pk
        }
        response = self.authorized_client.post(
            reverse(POST_EDIT_URL_NAME, kwargs={'post_id': post.pk}),
            data=form_data
        )
        self.assertRedirects(
            response,
            reverse(POST_DETAIL_URL_NAME, kwargs={'post_id': post.pk})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(Post.objects.first().text, form_data['text'])
        self.assertEqual(Post.objects.first().group.pk, form_data['group'])
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_add_comment(self):
        '''Проверка добавления комментария'''
        post = Post.objects.create(
            text='Test text',
            author=self.user,
            group=self.group
        )
        comment_count = Comment.objects.count()
        form_data = {
            'author': self.user,
            'text': 'Тестовый комментарий'
        }
        response = self.authorized_client.post(
            reverse(ADD_COMMENT_URL_NAME, args=(post.pk,)),
            data=form_data,
            follow=True
        )
        comment = Comment.objects.first()
        self.assertRedirects(
            response,
            reverse(POST_DETAIL_URL_NAME, args=(post.pk,))
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(Comment.objects.filter(
            text='Тестовый комментарий',
            author=self.user).exists())
        self.assertEqual(comment.author, form_data['author'])
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_add_comment_guest_client(self):
        '''Проверка создания комментария неавторизованным пользователем'''
        post = Post.objects.create(
            text='Test text',
            author=self.user,
            group=self.group
        )
        form_data = {
            'author': self.user,
            'text': 'Тестовый комментарий'
        }
        response = self.guest_client.post(
            reverse(ADD_COMMENT_URL_NAME, args=(post.pk,)),
            data=form_data,
            follow=True
        )
        self.assertIsNone(Comment.objects.first())
        self.assertRedirects(
            response,
            (reverse('users:login') + '?next='
                + reverse('posts:add_comment', args=(post.pk,)))
        )
