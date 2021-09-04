from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class URLsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовое название сообщества',
            slug='test-slug'
        )

        cls.post_author = User.objects.create_user('tania_ov')

        cls.post = Post.objects.create(
            text='Это тестовый текст для тестирования модели Post',
            author=cls.post_author
        )

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.create_user(username='petia_iv')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.post_author = URLsTest.post_author
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post_author)

        self.group = URLsTest.group

    def test_page_available_for_unauth_user(self):
        urls_and_expected_status_codes = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.post_author.username}/': HTTPStatus.OK,
        }
        for (url, status_code) in urls_and_expected_status_codes.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_page_available_for_auth_user(self):
        urls_and_expected_status_codes = {
            '/create/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
        }
        for (url, status_code) in urls_and_expected_status_codes.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)

        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_available_for_post_author(self):
        response = self.authorized_author.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_happens_unauth_user(self):
        urls_and_expected_status_codes = {
            '/create/': HTTPStatus.FOUND,
            f'/posts/{self.post.id}/edit/':
            HTTPStatus.FOUND
        }
        for (url, status_code) in urls_and_expected_status_codes.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_redirect_happens_unauth_user(self):
        urls_and_expected_redirect_pages = {
            '/create/': '/auth/login/?next=/create/',

            f'/posts/{self.post.id}/edit/':
            '/auth/login/?next=/'
            f'posts/{self.post.id}/edit/'
        }
        for (url, redirect_page) in urls_and_expected_redirect_pages.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect_page)

    def test_redirect_happens_auth_user(self):
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/edit/', follow=True
        )
        self.assertRedirects(
            response, f'/posts/{self.post.id}/'
        )

    def test_urls_correct_templates_usage(self):
        urls_and_corresponding_templates = {
            '/': 'index.html',
            f'/group/{self.group.slug}/': 'group.html',
            '/create/': 'new_post.html',

            f'/posts/{self.post.id}/edit/':
            'new_post.html'
        }
        for url, template in urls_and_corresponding_templates.items():
            with self.subTest(url=url):
                response = self.authorized_author.get(url)
                self.assertTemplateUsed(response, template)
