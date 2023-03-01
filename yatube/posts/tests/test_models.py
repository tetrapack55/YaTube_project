from django.test import TestCase

from posts.models import Comment, Follow, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.following_user = User.objects.create_user(username='Following')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.following_user
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        object_names = {
            self.post.text[:15]: str(self.post),
            self.group.title: str(self.group),
            self.comment.text[:15]: str(self.comment)
        }
        for expected_name, value in object_names.items():
            with self.subTest(value=value):
                self.assertEqual(expected_name, value)

    def test_models_have_correct_verbose_names(self):
        """verbose_name в полях моделей совпадает с ожидаемым."""
        verbose_data = (
            ('text', 'Текст',
                self.post._meta.get_field('text').verbose_name),
            ('pub_date', 'Дата публикации',
                self.post._meta.get_field('pub_date').verbose_name),
            ('author', 'Автор',
                self.post._meta.get_field('author').verbose_name),
            ('group', 'Группа',
                self.post._meta.get_field('group').verbose_name),
            ('image', 'Картинка',
                self.post._meta.get_field('image').verbose_name),
            ('title', 'Название группы',
                self.group._meta.get_field('title').verbose_name),
            ('slug', 'Адрес группы',
                self.group._meta.get_field('slug').verbose_name),
            ('description', 'Описание группы',
                self.group._meta.get_field('description').verbose_name),
            ('post', 'Комментарий',
                self.comment._meta.get_field('post').verbose_name),
            ('author', 'Автор комментария',
                self.comment._meta.get_field('author').verbose_name),
            ('text', 'Текст комментария',
                self.comment._meta.get_field('text').verbose_name),
            ('created', 'Дата публикации комментария',
                self.comment._meta.get_field('created').verbose_name),
            ('user', 'Подписчик',
                self.follow._meta.get_field('user').verbose_name),
            ('author', 'Автор',
                self.follow._meta.get_field('author').verbose_name)
        )
        for field, expected_value, verbose in verbose_data:
            with self.subTest(field=field):
                self.assertEqual(
                    verbose, expected_value
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        help_text_data = (
            ('text', 'Введите текст',
                self.post._meta.get_field('text').help_text),
            ('group', 'Группа, к которой будет относиться пост',
                self.post._meta.get_field('group').help_text),
            ('text', 'Введите комментарий',
                self.comment._meta.get_field('text').help_text)
        )
        for field, expected_value, h_text in help_text_data:
            with self.subTest(field=field):
                self.assertEqual(h_text, expected_value)
