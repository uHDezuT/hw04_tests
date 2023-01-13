from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm
from .models import Post, Group, User

SELECT_LIMIT = 10  # лимит постов на странице


def paginator(request, posts):
    paginator = Paginator(posts, SELECT_LIMIT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page


def index(request):
    """Главная страница проекта yatube."""

    posts = Post.objects.all()
    page = paginator(request, posts)
    context = {
        'page_obj': page,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Страница постов определённой группы."""

    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)[:10]
    page = paginator(request, posts)
    context = {
        "group": group,
        "page_obj": page,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    """Страница профиля пользователя проекта yatube."""

    user = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user)
    posts_count = post_list.count()
    page = paginator(request, post_list)
    context = {
        "author": user,
        "page_obj": page,
        "posts_count": posts_count,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    """Страница с описанием поста."""

    user_post = get_object_or_404(Post, id=post_id)
    post_count = user_post.author.posts.count()
    context = {
        'post_count': post_count,
        'user_post': user_post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Страница создания поста."""

    title = "Добавить запись"
    button_caption = "Добавить"
    form = PostForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", username=request.user)
    form = PostForm()
    return render(request, "posts/create_post.html",
                  {"form": form,
                   "title": title,
                   "button_caption": button_caption})


@login_required
def post_edit(request, post_id):
    """Страница редактирования поста."""

    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect("posts:post_detail",
                        post_id=post_id)
    title = "Редактировать запись"
    button_caption = "Сохранить"
    form = PostForm(request.POST or None, instance=post)
    if request.method == "POST" and form.is_valid():
        form.text = form.cleaned_data['text']
        form.group = form.cleaned_data['group']
        form.author = request.user
        form.save()
        return redirect("posts:post_detail",
                        post_id=post_id)
    return render(request,
                  "posts/create_post.html", {
                      "form": form,
                      "title": title,
                      "button_caption": button_caption,
                      "post": post})
