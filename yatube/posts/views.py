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
    page_obj = paginator.get_page(page_number)

    return render(request, 'index.html', {'page_obj': page_obj})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_posts_list = group.posts.all()
    paginator = Paginator(group_posts_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,
                  'group.html',
                  {'group': group, 'page_obj': page_obj})


def profile(request, username):
    a_user = get_object_or_404(User, username=username)
    a_users_posts = a_user.posts.all()
    paginator = Paginator(a_users_posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'a_user': a_user,
        'page_obj': page,
        'profile_view': True,
    }

    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=a_user
        ).exists()

        context['following'] = following

    if request.user.username == username:
        self_following = True
        editing_permitted = True

        context['self_following'] = self_following
        context['editing_permitted'] = editing_permitted

    return render(request, 'profile.html', context)


@login_required
def post_view(request, post_id):
    a_post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    comments = a_post.comments.all()
    a_user = a_post.author
    context = {
        'a_post': a_post,
        'post_view': True,
        'form': form,
        'comments': comments,
        'post_id': post_id,
        'a_user': a_user,
    }

    if request.user.username == a_post.author.username:
        editing_permitted = True
        context['editing_permitted'] = editing_permitted

    return render(request, 'post.html', context)


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
def post_edit(request, post_id):

    post_to_be_edited = get_object_or_404(Post, id=post_id)

    if request.user != post_to_be_edited.author:
        return redirect('post', post_id=post_id)

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post_to_be_edited)

    if form.is_valid():
        form.save()
        return redirect('post', post_id=post_id)

    return render(
        request,
        'new_post.html',
        {'form': form, 'editing': True,
         'post_id': post_id}
    )


@login_required
def add_comment(request, post_id):

    post_to_be_commented = get_object_or_404(Post, id=post_id)

    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post_to_be_commented
        comment.save()

    return redirect('post', post_id=post_id)


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
    Follow.objects.get_or_create(
        user=request.user, author=author_to_be_followed
    )

    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    followed_author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=followed_author).delete()

    return redirect('profile', username=username)
