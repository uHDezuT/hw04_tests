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
            title='Новая группа',
            slug='slug',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Новый пост',
        )
        cls.long_post = Post.objects.create(
            author=cls.user,
            text="Не более 15 символов может уместиться в превью"
        )

    def test_model_post_have_correct_object_names(self):
        """У модели Post корректно работает __str__."""
        post = PostModelTest.post
        long_post = PostModelTest.long_post
        self.assertEqual(str(long_post), "Не более 15 сим")
        self.assertEqual(str(post), "Новый пост")

    def test_model_group_have_correct_object_names(self):
        """У модели Group корректно работает __str__."""
        post_group = PostModelTest.group
        expected_object_name_group = post_group.title
        self.assertEqual(expected_object_name_group, str(post_group))

    def test_Posts_verbose_name(self):
        """verbose_name совпадает с ожидаемым."""
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
        """help_text совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_text = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(post._meta.get_field(field).help_text,
                                 value)
