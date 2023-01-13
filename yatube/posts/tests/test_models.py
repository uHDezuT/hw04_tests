from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post_group = PostModelTest.group
        expected_object_name_group = post_group.title
        self.assertEqual(expected_object_name_group, str(post_group))

        post = PostModelTest.post
        expected_object_name_post = post.text[:15]
        self.assertEqual(expected_object_name_post, str(post))

    def test_Posts_verbose_name(self):
        """Проверяем verbose_name на совпадение с ожидаемыми."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(post._meta.get_field(field).verbose_name,
                                 value)

    def test_Posts_help_text(self):
        """Проверяем help_text на совпадение с ожидаемыми."""
        post = PostModelTest.post
        field_help_text = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(post._meta.get_field(field).help_text,
                                 value)
