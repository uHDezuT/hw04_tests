from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, User


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='post_author',
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=PostPagesTests.user,
            group=PostPagesTests.group,
        )
        cls.group_fake = Group.objects.create(
            title='Фейковая группа',
            slug='fake-slug',
            description='Описание фейк группы',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_views_use_correct_template(self):
        """URL-адреса использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={
                        'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={
                        'username': self.user.username}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={
                        'post_id': self.post.id}): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': self.post.id}): 'posts/create_post.html',
            reverse('posts:post_create', ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Проверка соответствия ожидаемого словаря context,
        передаваемого в шаблон при вызове(с пажинатором)."""
        context = {reverse('posts:index'): self.post,
                   reverse('posts:group_list',
                           kwargs={'slug': self.group.slug,
                                   }): self.post,
                   reverse('posts:profile',
                           kwargs={'username': self.user.username,
                                   }): self.post,
                   }
        for reverse_page, post_object in context.items():
            with self.subTest(reverse_page=reverse_page):
                response = self.authorized_client.get(reverse_page)
                page_object = response.context['page_obj'][0]
                self.assertEqual(page_object.text, post_object.text)
                self.assertEqual(page_object.pub_date, post_object.pub_date)
                self.assertEqual(page_object.author, post_object.author)
                self.assertEqual(page_object.group, post_object.group)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        context = {reverse('posts:group_list',
                           kwargs={'slug': self.group.slug}): self.group,
                   }
        for reverse_page, group in context.items():
            with self.subTest(reverse_page=reverse_page):
                response = self.authorized_client.get(reverse_page)
                group_object = response.context['group']
                self.assertEqual(group_object.title, group.title)
                self.assertEqual(group_object.slug, group.slug)
                self.assertEqual(group_object.description,
                                 group.description)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        context = {reverse('posts:profile',
                           kwargs={'username': self.user.username}): self.user,
                   }
        for reverse_page, user in context.items():
            with self.subTest(reverse_page=reverse_page):
                response = self.authorized_client.get(reverse_page)
                author_object = response.context['author']
                self.assertEqual(author_object.id, user.id)
                self.assertEqual(author_object.username, user.username)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        context = {reverse('posts:post_detail',
                           kwargs={'post_id': self.post.id}): self.user,
                   }
        for reverse_page, user_post in context.items():
            with self.subTest(reverse_page=reverse_page):
                response = self.authorized_client.get(reverse_page)
                author_object = response.context['user_post']
                self.assertEqual(author_object.id, user_post.id)
                self.assertEqual(author_object.author.username,
                                 user_post.username)

    def test_post_edit_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_create_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_new_post_in_group(self):
        """Пост сохраняется в группе."""
        posts_count = Post.objects.filter(group=self.group).count()
        Post.objects.create(
            text='Текст нового поста для теста сохранения в группе',
            author=self.user,
            group=self.group,
        )
        self.assertNotEqual(Post.objects.filter(
            group=self.group).count(), posts_count)

    def test_new_post_not_in_another_group(self):
        """Пост не сохраняется в группе, не предназначенной для него."""
        posts_count = Post.objects.filter(group=self.group_fake).count()
        Post.objects.create(
            text='Тестовый текст для нового поста',
            author=self.user,
            group=self.group,
        )
        self.assertEqual(Post.objects.filter(
            group=self.group_fake).count(), posts_count)

    def test_new_post_in_main_group_list_profile_pages(self):
        """Пост появляется на главной странице,
         странице пользователя и странице групп при указании группы"""
        response_dict = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        }
        for reverse_obj in response_dict:
            response = self.authorized_client.get(reverse_obj)
            post_count = len(response.context.get('page_obj').object_list)
            Post.objects.create(
                text='Тестовый текст для нового поста',
                author=self.user,
                group=self.group,
            )
            response = self.authorized_client.get(reverse_obj)
            post_count1 = len(response.context.get('page_obj').object_list)
            self.assertEqual(post_count + 1, post_count1)
            Post.objects.filter(
                text='Тестовый текст для нового поста').delete()
