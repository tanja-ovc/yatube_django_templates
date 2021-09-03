from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        labels = {
            'text': ('Текст записи'),
            'group': ('Сообщество'),
        }
        help_texts = {
            'text': ('Введите здесь ваш текст.'),
            'group': ('Выберите сообщество для публикации вашего поста.'),
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': ('Текст комментария'),
        }
        help_texts = {
            'text': ('Введите здесь ваш комментарий'),
        }
