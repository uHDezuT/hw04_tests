from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Новое название группы',
            slug='slug',
            description='Новое описание группы',
        )
        cls.user = User.objects.create_user(
            username='post_author'
        )
        cls.user_2 = User.objects.create_user(
            username='another_user'
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=StaticURLTests.user,
            group=StaticURLTests.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.post_author = Client()
        self.post_author.force_login(self.user)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_2)

    def test_guest_client_urls_status_code(self):
        """Адреса для НЕ авторизированного пользователя."""
        field_response_urls_code = {
            '/': 200,
            '/group/slug/': 200,
            '/group/fake_slug/': 404,
            '/profile/post_author/': 200,
            '/create/': 302,
            '/posts/1/edit/': 302,
            '/fake_author/': 404,
            '/fake_author/1/': 404,
        }
        for url, response_code in field_response_urls_code.items():
            with self.subTest(url=url):
                status_code = self.guest_client.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_authorized_client_urls_status_code(self):
        """Адреса для Авторизированного пользователя."""
        field_response_urls_code = {
            '/': 200,
            '/group/slug/': 200,
            '/group/fake_slug/': 404,
            '/profile/post_author/': 200,
            '/create/': 200,
            '/posts/1/edit/': 200,
            '/fake_author/': 404,
            '/fake_author/1/': 404,
        }
        for url, response_code in field_response_urls_code.items():
            with self.subTest(url=url):
                status_code = self.post_author.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)
