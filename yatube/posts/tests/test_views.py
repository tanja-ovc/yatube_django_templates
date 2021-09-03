import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from http import HTTPStatus

from posts.models import Comment, Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Тестовое название сообщества',
            slug='test-slug'
        )

        cls.post_author = User.objects.create_user('tania_o')

        # Для тестирования загрузки изображений
        # берём байт-последовательность картинки,
        # состоящей из двух пикселей: белого и чёрного
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            text='Это текст для тестирования модели Post',
            author=cls.post_author,
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок, файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='petia_i')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.post_author = ViewsTest.post_author
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post_author)

        self.post = ViewsTest.post

        self.group = ViewsTest.group

    def test_views_correct_templates_usage(self):
        """View-функция использует соответствующий шаблон."""
        views_names_and_corresponding_templates = {
            reverse('index'): 'index.html',
            reverse('group_posts',
                    kwargs={'slug': self.group.slug}): 'group.html',
            reverse('new_post'): 'new_post.html',

            reverse(
                'post_edit', kwargs={'username': self.post_author.username,
                                     'post_id': self.post.id}
            ): 'new_post.html',

            reverse(
                'profile', kwargs={'username': self.post_author.username}
            ): 'profile.html',

            reverse(
                'post', kwargs={'username': self.post_author.username,
                                'post_id': self.post.id}
            ): 'post.html',
        }

        for (reverse_name,
             template) in views_names_and_corresponding_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверка словаря контекста страницы создания поста
    # (в нём передаётся форма)
    def test_new_post_correct_context_usage(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'text': forms.fields.CharField,
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            'group': forms.fields.ChoiceField,
        }

        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    # Проверяем, что словарь context главной страницы
    # в первом элементе списка page содержит ожидаемые
    # значения
    def test_homepage_correct_context_usage(self):
        """Шаблон index.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post_author.username)
        self.assertEqual(post_image_0, self.post.image)

    # Проверяем, что словарь context страницы сообщества 'group/<slug:slug>/'
    # содержит ожидаемые значения
    def test_group_page_correct_context_usage(self):
        """Шаблон group.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(
            response.context['group'].title, self.group.title
        )
        self.assertEqual(response.context['group'].slug, self.group.slug)

        first_object = response.context['page'][0]
        self.assertEqual(first_object.image, self.post.image)

    # Проверка словаря контекста страницы редактирования поста
    # (в нём передаётся форма)
    def test_edit_post_correct_context_usage(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_author.get(reverse('new_post'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'text': forms.fields.CharField,
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            'group': forms.fields.ChoiceField,
        }

        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    # Проверяем, что словарь context страницы профайла
    # в первом элементе списка page содержит ожидаемые
    # значения
    def test_profile_correct_context_usage(self):
        """Шаблон profile.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': self.post_author.username})
        )
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post_author.username)
        self.assertEqual(post_image_0, self.post.image)

    # Проверяем, что словарь context страницы отдельного поста
    # содержит ожидаемые значения
    def test_one_post_page_correct_context_usage(self):
        """Шаблон post.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post', kwargs={
                'username': self.post_author.username, 'post_id': self.post.id
            })
        )
        self.assertEqual(response.context['a_post'].text, self.post.text)
        self.assertEqual(response.context['a_post'].author.username,
                         self.post_author.username)
        self.assertEqual(response.context['a_post'].image, self.post.image)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Тестовое название сообщества',
            slug='test_slug'
        )

        cls.posts_author = User.objects.create_user('tanja_ov')

        for post in range(0, 13):
            cls.post = Post.objects.create(
                text=(
                    'Тестовый пост для главной страницы, сообщества и профиля'
                ),
                author=cls.posts_author,
                group=cls.group
            )

    def setUp(self):
        self.guest_client = Client()

        self.posts_author = PaginatorViewsTest.posts_author

        self.group = PaginatorViewsTest.group

        self.first_page = {
            reverse('index'): 10,
            reverse('group_posts', kwargs={'slug': self.group.slug}): 10,
            reverse('profile',
                    kwargs={'username': self.posts_author.username}): 10
        }

        self.second_page = {
            reverse('index'): 3,
            reverse('group_posts', kwargs={'slug': self.group.slug}): 3,
            reverse('profile',
                    kwargs={'username': self.posts_author.username}): 3
        }

    def test_first_page_contains_ten_records(self):
        for url_name_reverse, posts_amount in self.first_page.items():
            response = self.guest_client.get(url_name_reverse)
            self.assertEqual(
                len(response.context['page'].object_list), posts_amount
            )

    def test_second_page_contains_three_records(self):
        for url_name_reverse, posts_amount in self.second_page.items():
            response = self.guest_client.get(url_name_reverse + '?page=2')
            self.assertEqual(
                len(response.context['page'].object_list), posts_amount
            )


class TestPostAdded(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group1 = Group.objects.create(
            title='Сообщество 1 тест',
            slug='test-slug1'
        )
        cls.group2 = Group.objects.create(
            title='Сообщество 2 тест',
            slug='test-slug2'
        )
        cls.user = User.objects.create_user('petia_ivanov')

        cls.post1 = Post.objects.create(
            text='Текст поста для добавления в 1-ую группу, '
                 'а также на главную страницу.',
            author=cls.user,
            group=cls.group1
        )
        cls.post2 = Post.objects.create(
            text='Текст поста для добавления во 2-ую группу, '
                 'а также на главную страницу.',
            author=cls.user,
            group=cls.group2
        )

    def setUp(self):
        self.guest_client = Client()
        self.added_post = TestPostAdded.post1
        self.group1 = TestPostAdded.group1
        self.group2 = TestPostAdded.group2

    def test_post_added_to_homepage(self):
        response = self.guest_client.get(reverse('index'))
        posts_list_homepage = response.context['page'].object_list

        self.assertIn(self.added_post, posts_list_homepage)

    def test_post_added_to_a_group(self):
        response = self.guest_client.get(
            reverse('group_posts', kwargs={'slug': self.group1.slug})
        )
        latest_post_group1 = response.context['page'].object_list[0]

        self.assertEqual(latest_post_group1.text, self.added_post.text)
        self.assertEqual(latest_post_group1.group, self.added_post.group)

    def test_post_not_added_to_a_wrong_group(self):
        response = self.guest_client.get(
            reverse('group_posts', kwargs={'slug': self.group2.slug})
        )
        latest_post_group2 = response.context['page'].object_list[0]

        self.assertNotEqual(latest_post_group2.text, self.added_post.text)
        self.assertNotEqual(latest_post_group2.group, self.added_post.group)


class TestCommentsAdded(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_post_author = User.objects.create_user('vasia_petrov')
        cls.user_commentator = User.objects.create_user('zhenia_vasechkin')

        cls.post = Post.objects.create(
            text='Пост - тест',
            author=cls.user_post_author,
        )

        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user_commentator,
            text='Комментарий - тест',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_commentator)

        self.user_post_author = TestCommentsAdded.user_post_author
        self.post = TestCommentsAdded.post

    def test_comment_added_to_post(self):
        response = self.authorized_client.get(
            f'/{self.user_post_author.username}/{self.post.id}/'
        )
        added_comments = response.context['comments'][0]

        self.assertEqual(added_comments, self.post.comments.first())


class TestCache(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user('Mr. Cache')

        cls.post = Post.objects.create(
            text='Текст поста для тестирования кэша.',
            author=cls.user,
        )

    def setUp(self):
        self.post = TestCache.post
        self.guest_client = Client()

    def test_cache(self):

        response = self.guest_client.get(reverse('index'))
        posts_list_homepage = response.context['page'].object_list
        self.assertIn(self.post, posts_list_homepage)

        self.post.delete()

        self.assertIn(str.encode(f'{self.post}'), response.content)

        cache.clear()

        response_cache_cleared = self.guest_client.get(reverse('index'))

        self.assertNotIn(
            str.encode(f'{self.post}'), response_cache_cleared.content
        )


class Test404(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_error_page(self):
        response = self.guest_client.get('/nonexist-page/')
        # Проверьте, что статус ответа сервера - 404
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Проверьте, что используется шаблон core/404.html
        self.assertTemplateUsed(response, 'core/404.html')


class TestFollow(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.follower = User.objects.create_user('stanislav')

        cls.author_to_be_followed = User.objects.create_user('dostoevsky')

        cls.not_a_follower = User.objects.create_user('i_am_not_subscribed')

        cls.subscription = Follow.objects.create(
            user=cls.follower, author=cls.author_to_be_followed
        )

        cls.post = Post.objects.create(
            text='Текст поста автора, на которого подписаны.',
            author=cls.author_to_be_followed,
        )

    def setUp(self):
        self.follower = TestFollow.follower
        self.author_to_be_followed = TestFollow.author_to_be_followed
        self.not_a_follower = TestFollow.not_a_follower

        self.authorized_follower = Client()
        self.authorized_follower.force_login(self.follower)

        self.authorized_not_a_follower = Client()
        self.authorized_not_a_follower.force_login(self.not_a_follower)

        self.subscription = TestFollow.subscription
        self.post = TestFollow.post

    def test_follow_and_unfollow(self):
        Follow.objects.create(
            user=self.follower, author=self.author_to_be_followed
        )
        self.assertEqual(
            self.subscription, self.author_to_be_followed.following.first()
        )

        Follow.objects.filter(
            user=self.follower, author=self.author_to_be_followed
        ).delete()
        self.assertEqual(
            None, self.author_to_be_followed.following.first()
        )

    def test_posts_are_followed(self):

        Follow.objects.create(
            user=self.follower, author=self.author_to_be_followed
        )

        response = self.authorized_follower.get(reverse('follow_index'))
        latest_post_followed_by_follower = (
            response.context['page'][0]
        )
        self.assertEqual(latest_post_followed_by_follower.text, self.post.text)

        response = self.authorized_not_a_follower.get(reverse('follow_index'))
        latest_post_followed_by_not_a_follower = (
            response.context['page'][0]
        )
        self.assertNotEqual(
            latest_post_followed_by_not_a_follower.text, self.post.text
        )
