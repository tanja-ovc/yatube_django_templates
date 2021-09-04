import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.post_author = User.objects.create_user('tania_o')

        cls.post = Post.objects.create(
            text='Текст для нового поста: создание поста',
            author=cls.post_author
        )
        cls.form = PostForm()

        cls.group = Group.objects.create(
            title='Сообщество Test Forms',
            slug='test-forms-slug'
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
        self.guest_client = Client()

        self.user = User.objects.create_user(username='vasia_z')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.post_author = PostCreateFormTests.post_author
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post_author)

        self.post = PostCreateFormTests.post
        self.group = PostCreateFormTests.group

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

        self.form_data_new_post = {
            'text': 'Создание поста: тест',
            'group': self.group.id,
            'image': uploaded,
        }

        self.form_data_editing_post = {
            'text': 'Редактирование поста: тест',
            'group': self.group.id
        }

    def test_create_post(self):
        """Валидная форма создает пост."""
        posts_amount = Post.objects.count()

        response = self.authorized_client.post(
            reverse('new_post'),
            data=self.form_data_new_post,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'profile', kwargs={'username': self.user.username}
        ))
        self.assertEqual(Post.objects.count(), posts_amount + 1)
        self.assertTrue(
            Post.objects.filter(
                text=self.form_data_new_post['text'],
                group=self.form_data_new_post['group']
            ).exists()
        )

    def test_editing_post_is_successful(self):
        """Изменённый пост сохраняется в БД."""
        posts_amount = Post.objects.count()

        response = self.authorized_author.post(
            reverse(
                'post_edit', kwargs={'post_id': self.post.id}
            ),
            data=self.form_data_editing_post,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'post', kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(Post.objects.count(), posts_amount)
        self.assertTrue(
            Post.objects.filter(
                text=self.form_data_editing_post['text'],
                group=self.form_data_editing_post['group']
            ).exists()
        )
