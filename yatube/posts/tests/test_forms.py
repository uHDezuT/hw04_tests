from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(
            username='post_author',
        )

        cls.group = Group.objects.create(
            title='Новая группа',
            slug='slug',
            description='Описание группы'
        )

        cls.post = Post.objects.create(
            text='Новый пост',
            author=PostFormTests.user,
            group=PostFormTests.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_new_post_success(self):
        """Создание поста прошло успешно и запись сохранена в БД."""
        posts_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Новый текст поста',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username}))

        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """Редактирование поста post_id прошло успешно."""
        form_data = {
            'group': self.group.id,
            'text': 'Новый текст поста'
        }
        response = self.authorized_client.post(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            response.context['user_post'].text, form_data['text']
        )

    def test_signup(self):
        """При заполнении формы signup создаётся новый пользователь."""
        users_count = User.objects.count()
        form_data = {
            "username": 'Gregory',
            "email": 'dfsfsdf@mail.ru',
            "password1": 'Gre12345678',
            "password2": 'Gre12345678',
        }
        self.guest_client.post(reverse('users:signup'),
                               data=form_data,
                               follow=True
                               )
        self.assertEqual(User.objects.count(), users_count + 1)
