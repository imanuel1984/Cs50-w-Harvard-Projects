from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
import json

from .models import User, Post, Follow
from .forms import NewPostForm


# -----------------------------
# INDEX / ALL POSTS
# -----------------------------
def index(request):
    form = NewPostForm()
    posts_list = Post.objects.all()  # ordered by Post.Meta ordering
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # annotate each post with like status
    for post in page_obj:
        post.is_liked = request.user.is_authenticated and post.likes.filter(pk=request.user.pk).exists()

    return render(request, "network/index.html", {
        "form": form,
        "page_obj": page_obj
    })


# -----------------------------
# AUTHENTICATION
# -----------------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "network/login.html", {"message": "Invalid username or password."})
    return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return redirect("index")  # always redirect to index/home


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirmation = request.POST.get("confirmation")

        if password != confirmation:
            return render(request, "network/register.html", {"message": "Passwords must match."})

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
        except IntegrityError:
            return render(request, "network/register.html", {"message": "Username already taken."})

        login(request, user)
        return redirect("index")
    return render(request, "network/register.html")


# -----------------------------
# POSTS
# -----------------------------
@login_required
def create_post(request):
    if request.method == "POST":
        form = NewPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
    return redirect("index")


@login_required
@require_http_methods(["PUT"])
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return HttpResponseForbidden("Cannot edit others' posts.")

    try:
        data = json.loads(request.body)
        content = data.get("content", "").strip()
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    if not content:
        return JsonResponse({"error": "Content cannot be empty."}, status=400)

    post.content = content
    post.save()
    return JsonResponse({"message": "Updated", "content": post.content})


@login_required
@require_http_methods(["POST"])
def toggle_like(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = request.user

    if post.likes.filter(pk=user.pk).exists():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

    return JsonResponse({
        "liked": liked,
        "likes_count": post.likes.count()
    })


# -----------------------------
# FOLLOWING
# -----------------------------
@login_required
def following_posts(request):
    followed_ids = request.user.following.values_list("followed_id", flat=True)
    posts_list = Post.objects.filter(author_id__in=followed_ids)
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    for post in page_obj:
        post.is_liked = request.user.is_authenticated and post.likes.filter(pk=request.user.pk).exists()

    return render(request, "network/following.html", {"page_obj": page_obj})


@login_required
@require_http_methods(["POST"])
def toggle_follow(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return HttpResponseForbidden("Cannot follow yourself.")

    obj, created = Follow.objects.get_or_create(follower=request.user, followed=target)
    if not created:
        obj.delete()
        status = "unfollowed"
    else:
        status = "followed"

    return JsonResponse({"status": status, "followers_count": target.followers.count()})


# -----------------------------
# USER PROFILE
# -----------------------------
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts_list = profile_user.posts.all()
    paginator = Paginator(posts_list, 10)
    page_obj = paginator.get_page(request.GET.get("page", 1))

    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(follower=request.user, followed=profile_user).exists()

    followers_count = profile_user.followers.count()
    following_count = profile_user.following.count()

    for post in page_obj:
        post.is_liked = request.user.is_authenticated and post.likes.filter(pk=request.user.pk).exists()

    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "page_obj": page_obj,
        "is_following": is_following,
        "followers_count": followers_count,
        "following_count": following_count
    })
