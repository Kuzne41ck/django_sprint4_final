from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm, UserEditForm, UserRegisterForm
from .models import Category, Comment, Post

User = get_user_model()
POSTS_PER_PAGE = 10


def get_published_posts():
    return (
        Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )
        .select_related("author", "category", "location")
        .annotate(comment_count=Count("comments"))
        .order_by("-pub_date")
    )


def paginate_queryset(request, queryset):
    from django.core.paginator import Paginator

    paginator = Paginator(queryset, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def index(request):
    page_obj = paginate_queryset(request, get_published_posts())
    return render(request, "blog/index.html", {"page_obj": page_obj})


def category_posts(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, is_published=True)
    page_obj = paginate_queryset(
        request,
        get_published_posts().filter(category=category),
    )
    return render(
        request,
        "blog/category.html",
        {"category": category, "page_obj": page_obj},
    )


def get_post_for_view(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related("author", "category", "location"),
        pk=post_id,
    )
    if request.user == post.author:
        return post
    if (
        not post.is_published
        or post.pub_date > timezone.now()
        or not post.category
        or not post.category.is_published
    ):
        raise Http404
    return post


def post_detail(request, post_id):
    post = get_post_for_view(request, post_id)
    comments = post.comments.select_related("author").order_by("created_at")
    form = CommentForm()
    return render(
        request,
        "blog/detail.html",
        {"post": post, "comments": comments, "form": form},
    )


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = (
        Post.objects.filter(author=profile_user)
        .select_related("author", "category", "location")
        .annotate(comment_count=Count("comments"))
        .order_by("-pub_date")
    )
    if request.user != profile_user:
        posts = posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )
    page_obj = paginate_queryset(request, posts)
    return render(
        request,
        "blog/profile.html",
        {"profile": profile_user, "page_obj": page_obj},
    )


def registration(request):
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("login")
    return render(request, "registration/registration_form.html", {"form": form})


@login_required
def edit_profile(request):
    form = UserEditForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect("blog:profile", username=request.user.username)
    return render(request, "blog/user.html", {"form": form})


@login_required
def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("blog:profile", username=request.user.username)
    return render(request, "blog/create.html", {"form": form})


def redirect_if_not_author(request, post):
    if request.user != post.author:
        return redirect("blog:post_detail", post_id=post.pk)
    return None


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    redirect_response = redirect_if_not_author(request, post)
    if redirect_response:
        return redirect_response
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect("blog:post_detail", post_id=post.pk)
    return render(request, "blog/create.html", {"form": form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    redirect_response = redirect_if_not_author(request, post)
    if redirect_response:
        return redirect_response
    form = PostForm(instance=post)
    if request.method == "POST":
        post.delete()
        return redirect("blog:profile", username=request.user.username)
    return render(request, "blog/create.html", {"form": form})


@login_required
def add_comment(request, post_id):
    post = get_post_for_view(request, post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("blog:post_detail", post_id=post.pk)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect("blog:post_detail", post_id=post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect("blog:post_detail", post_id=post_id)
    return render(request, "blog/comment.html", {"form": form, "comment": comment})


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect("blog:post_detail", post_id=post_id)
    form = CommentForm(instance=comment)
    if request.method == "POST":
        comment.delete()
        return redirect("blog:post_detail", post_id=post_id)
    return render(request, "blog/comment.html", {"form": form, "comment": comment})
