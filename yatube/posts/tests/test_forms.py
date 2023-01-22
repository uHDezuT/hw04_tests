from django.core.files.uploadedfile import SimpleUploadedFile
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
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
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
            image=uploaded
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

    def test_profile_check_context_image(self):
        """Изображение передаётся в словаре context на страницу профайла"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        self.assertTrue(response.context['page_obj'][0].image)
        print(response.context['page_obj'][0].image)

    def test_index_check_context_image(self):
        """Изображение передаётся в словаре context на главную страницу"""
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertTrue(response.context['page_obj'][0].image)

    def test_group_list_check_context_image(self):
        """Изображение передаётся в словаре context на страницу группы"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.assertTrue(response.context['page_obj'][0].image)

    def test_post_detail_check_context_image(self):
        """Изображение передаётся в словаре context на страницу поста"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertTrue(response.context['user_post'].image)

    def test_new_post_with_image(self):
        """Создание поста с картинкой прошло успешно."""
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=PostFormTests.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'group': PostFormTests.group.id,
            'text': 'Новый пост2',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': self.post.author}))

        self.assertEqual(Post.objects.count(), posts_count + 1)
        print(Post.objects.filter(group=PostFormTests.group.id,
                                  text='Новый пост2',
                                  image=Post.objects.get(
                                      text='Новый пост2').image))
        self.assertTrue(
            Post.objects.filter(
                group=PostFormTests.group.id,
                text='Новый пост2',
                image=Post.objects.get(
                    text='Новый пост2').image,
            ).exists()
        )
