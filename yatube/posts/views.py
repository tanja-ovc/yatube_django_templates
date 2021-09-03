from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


def index(request):
    posts_list = Post.objects.all()
    paginator = Paginator(posts_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'index.html', {'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_posts_list = group.posts.all()
    paginator = Paginator(group_posts_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'group.html', {'group': group, 'page': page})


def profile(request, username):
    a_user = get_object_or_404(User, username=username)
    a_users_posts = a_user.posts.all()
    paginator = Paginator(a_users_posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    following = Follow.objects.filter(user=request.user,
                                      author=a_user).exists()

    return render(request, 'profile.html',
                  {'a_user': a_user, 'page': page, 'profile_view': True,
                   'following': following})


@login_required
def post_view(request, username, post_id):
    a_user = get_object_or_404(User, username=username)
    a_post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm()
    comments = a_post.comments.all()

    return render(request, 'post.html', {'a_post': a_post, 'post_view': True,
                                         'form': form, 'comments': comments,
                                         'username': username,
                                         'post_id': post_id,
                                         'a_user': a_user})


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            a_new_post = form.save(commit=False)
            a_new_post.author = request.user
            a_new_post.save()
            return redirect('index')

        return render(request, 'new_post.html', {'form': form})

    form = PostForm()
    return render(request, 'new_post.html', {'form': form})


@login_required
def post_edit(request, username, post_id):

    post_to_be_edited = get_object_or_404(
        Post, author__username=username, id=post_id
    )

    if request.user != post_to_be_edited.author:
        return redirect('post', username=username, post_id=post_id)

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post_to_be_edited)

    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)

    return render(
        request,
        'new_post.html',
        {'form': form, 'editing': True,
         'username': username, 'post_id': post_id}
    )


@login_required
def add_comment(request, username, post_id):

    post_to_be_commented = get_object_or_404(
        Post, author__username=username, id=post_id
    )

    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post_to_be_commented
        comment.save()

    return redirect('post', username=username, post_id=post_id)


@login_required
def follow_index(request):
    followed_posts_list = Post.objects.filter(
        author__following__user=request.user
    )
    paginator = Paginator(followed_posts_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {'page': page}

    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author_to_be_followed = get_object_or_404(User, username=username)
    Follow.objects.create(user=request.user, author=author_to_be_followed)

    return redirect('profile', username=username)

    # if request.user.username == username:
    #     return  # что-то о том, что на самого себя нельзя подписаться

    # Во view-функцию добавьте проверку: подписан ли текущий пользователь
    # на автора, страницу которого он просматривает; присвойте результат
    # проверки переменной following и передайте её в в словаре контекста
    # view-функции profile().


@login_required
def profile_unfollow(request, username):
    followed_author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=followed_author).delete()

    return redirect('profile', username=username)
