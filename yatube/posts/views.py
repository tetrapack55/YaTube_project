from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .models import Group, Follow, Post, User
from .forms import CommentForm, PostForm
from .utils import paginate


@cache_page(20, key_prefix='index_page')
def index(request):
    posts = Post.objects.select_related('author', 'group')
    return render(
        request,
        'posts/index.html',
        {'posts': posts, 'page_obj': paginate(request, posts)}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(
        request,
        'posts/group_list.html',
        {
            'group': group,
            'page_obj': paginate(
                request,
                group.posts.select_related('author', 'group')
            )
        }
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    return render(
        request,
        'posts/profile.html',
        {
            'author': author,
            'page_obj': paginate(
                request,
                author.posts.select_related('author', 'group')
            ),
            'following': (
                request.user.is_authenticated and Follow.objects.filter(
                    user=request.user.id, author=author
                ).exists()
            )
        }
    )


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'),
        pk=post_id
    )
    form = CommentForm(request.POST or None)
    return render(
        request,
        'posts/post_detail.html',
        {'post': post, 'form': form}
    )


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    context = {
        'form': form,
    }
    if not request.method == 'POST':
        return render(request, template, context)
    if not form.is_valid():
        return render(request, template, context)
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if post_id and request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'is_edit': True}
    )


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.select_related('author', 'group').filter(
        author__following__user=request.user)
    return render(
        request,
        'posts/follow.html',
        {'page_obj': paginate(request, posts)}
    )


@login_required
def profile_follow(request, username):
    following = get_object_or_404(User, username=username)
    if request.user != following:
        Follow.objects.get_or_create(user=request.user, author=following)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author)
    if follow.exists():
        follow.delete()
    return redirect('posts:profile', username)
