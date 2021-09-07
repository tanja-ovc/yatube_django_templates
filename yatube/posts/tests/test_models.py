from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class StrModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        user = User.objects.create_user('Таня')

        cls.post = Post.objects.create(
            text='Это тестовый текст для тестирования модели Post',
            author=user
        )

        cls.group = Group.objects.create(
            title='Тестовое название сообщества',
            slug='test-slug'
        )

    def test_str_post(self):
        """Проверка работы метода __str__ модели Post."""
        post_str = str(StrModelTest.post)
        post_text_trunc = StrModelTest.post.text[:15]
        expected_output = f'{post_text_trunc}...'
        self.assertEqual(post_str, expected_output,
                         'Метод __str__ модели Post работает неправильно')

    def test_str_group(self):
        """Проверка работы метода __str__ модели Group."""
        group_str = str(StrModelTest.group)
        expected_output = StrModelTest.group.title
        self.assertEqual(group_str, expected_output,
                         'Метод __str__ модели Group работает неправильно')
