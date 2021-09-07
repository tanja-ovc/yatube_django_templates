from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        blank=False, null=False, verbose_name='текст поста'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='дата публикации'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts',
        verbose_name='автор поста'
    )
    group = models.ForeignKey(
        'Group', on_delete=models.SET_NULL, related_name='posts',
        blank=True, null=True, verbose_name='относится к сообществу'
    )

    image = models.ImageField(
        upload_to='posts/', blank=True, verbose_name='изображение'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self):
        presenting_post_title = self.text[:15]
        return f'{presenting_post_title}...'


class Group(models.Model):
    title = models.CharField(
        max_length=200, verbose_name='название сообщества'
    )
    slug = models.SlugField(unique=True, verbose_name='slug')
    description = models.TextField(verbose_name='описание сообщества')

    class Meta:
        verbose_name = 'cообщество'
        verbose_name_plural = 'cообщества'

    def __str__(self):
        return f'{self.title}'


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments',
        verbose_name='относится к посту'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments',
        verbose_name='автор комментария'
    )
    text = models.TextField(verbose_name='текст комментария')
    created = models.DateTimeField(
        auto_now_add=True, verbose_name='дата публикации'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self):
        comment_text = self.text[:20]
        comment_view = (f'{comment_text}... (к записи "{self.post}..." '
                        f'автора {self.post.author})')
        return comment_view


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower',
        verbose_name='подписчик'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following',
        verbose_name='подписан(а) на'
    )

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'author'],
                       name='unique_subscription')]
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'

    def __str__(self):
        follow_view = f'Подписка {self.user} на {self.author}'
        return follow_view
