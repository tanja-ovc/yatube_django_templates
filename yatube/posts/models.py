from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(blank=False, null=False)
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts'
    )
    group = models.ForeignKey(
        'Group', on_delete=models.SET_NULL, related_name='posts',
        blank=True, null=True
    )

    image = models.ImageField('Картинка', upload_to='posts/', blank=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        presenting_post_title = self.text[:15]
        return f'{presenting_post_title}'


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return f'{self.title}'


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments',
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments'
    )
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        comment_view = self.text[:15]
        return f'{comment_view}'


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following'
    )
