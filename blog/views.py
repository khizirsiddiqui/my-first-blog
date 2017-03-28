from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect

from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from django.contrib import messages

from django.forms.models import inlineformset_factory

from django.core.exceptions import PermissionDenied

from .forms import PostForm, CommentForm, UserProfileForm, LoginForm
from .models import Post, Comment, UserProfile, Tag


def latest_posts():
    return Post.objects.filter(
        published_date__lte=timezone.now()).order_by('-views')


def recent_posts():
    return Post.objects.filter(
        published_date__lte=timezone.now()).order_by('-published_date')[0:3]


def post_list(request):
    return render(request, 'blog/post_list.html',
                  {'posts': latest_posts, 'recent': recent_posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.views += 1
    post.save()
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user.get_full_name()
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/post_detail.html',
                  {'post': post, 'form': form, 'recent': recent_posts})


@login_required
def post_upvote(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = request.user
    if user.is_authenticated:
        dec = post.upvote(user)
        if dec:
            messages.add_message(
                request, messages.SUCCESS, 'Post Upvoted')
        else:
            messages.add_message(
                request, messages.ERROR, 'Post already Upvoted')
        return render(request, 'blog/post_detail.html',
                      {'post': post, 'recent': recent_posts})
    else:
        messages.add_message(
            request, messages.ERROR, 'Please login/register to Upvote')
        return redirect('user_login')


@login_required
def rep_author(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user.is_authenticated:
        author = post.author
        authorProfile = UserProfile.objects.get(user=author)
        if request.user not in authorProfile.Likers.all():
            authorProfile.repAdd(liker=request.user)
            messages.add_message(
                request, messages.SUCCESS, 'Author Upvoted')
            return render(request, 'blog/post_detail.html',
                          {'post': post, 'recent': recent_posts})
        else:
            messages.add_message(
                request, messages.INFO, 'Author already Upvoted')
            return render(request, 'blog/post_detail.html',
                          {'post': post, 'recent': recent_posts})
    else:
        messages.add_message(
            request, messages.ERROR, 'Please login/register to Upvote')
        return redirect('user_login')


@login_required
def post_new(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect('post_detail', pk=post.pk)
        else:
            form = PostForm()
        return render(request, 'blog/post_edit.html',
                      {'form': form, 'recent': recent_posts})
    else:
        messages.add_message(
            request, messages.ERROR, 'Please login/register to Upvote')
        return redirect('user_login')


@login_required
def post_edit(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)
        if post.author.username == request.user.username:
            if request.method == "POST":
                form = PostForm(request.POST, instance=post)
                if form.is_valid():
                    post = form.save(commit=False)
                    post.author = request.user
                    post.save()
                    return redirect('post_detail', pk=post.pk)
            else:
                form = PostForm(instance=post)
            return render(request, 'blog/post_edit.html',
                          {'form': form, 'post': post, 'recent': recent_posts})
        else:
            return render(request, 'blog/post_detail.html',
                          {'post': post, 'recent': recent_posts})
    else:
        messages.add_message(
            request, messages.ERROR, 'Please login/register to Upvote')
        return redirect('user_login')


@login_required
def post_remove(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)
        if request.user.username == post.author.username:
            post.delete()
            messages.add_message(
                request, messages.INFO, 'Post Deleted')
            return render(request, 'blog/post_list.html',
                          {'posts': latest_posts, 'recent': recent_posts})
    else:
        messages.add_message(
            request, messages.ERROR, 'Please login/register to Upvote')
        return redirect('user_login')


def post_draft_list(request):
    if request.user.is_authenticated:
        posts = Post.objects.filter(
            published_date__isnull=True,
            author=request.user).order_by('created_date')
        return render(request, 'blog/post_draft_list.html',
                      {'posts': posts, 'recent': recent_posts})
    else:
        messages.add_message(
            request, messages.ERROR, 'Please login/register to Upvote')
        return redirect('user_login')


def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail', pk=post_pk)


def user_register(request):
    errors = []
    if request.POST:
        username = request.POST['username']
        if len(User.objects.filter(username=username)) == 0:
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            first_name = request.POST['fname']
            last_name = request.POST['lname']
            email = request.POST['email']
            if password1 == password2:
                user = User()
                user.username = username
                user.password = make_password(password1)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.save()
                print("New User registered: " + username)
                user = authenticate(username=username, password=password1)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return redirect('/')
            else:
                errors = ['Passwords dont match. Try again']
        else:
            errors = ['Username unavailable. Try another']
    return render(request, 'account/signup.html',
                  {'errors': errors, 'recent': recent_posts})


def user_login(request):
    form = LoginForm()
    auth_user = None
    userid = None
    password = None
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    else:
        if request.method == "POST":
            form = LoginForm(request.POST)

            if form.is_valid():
                userid = form.cleaned_data['username']
                password = form.cleaned_data['password']
                auth_user = authenticate(username=userid, password=password)
                if auth_user is not None and auth_user.is_active:
                    login(request, auth_user)
                    messages.add_message(
                        request, messages.SUCCESS, 'Successfuly Signed In')
                    return HttpResponseRedirect('/')

        else:
            form = LoginForm()

    return render(request, 'account/login.html', {'formset': form})


@login_required
def user_logout(request):
    logout(request)
    messages.add_message(
        request, messages.SUCCESS, 'Successfuly Signed out')
    return render(request, 'blog/post_list.html',
                  {'posts': latest_posts, 'recent': recent_posts})


@login_required
def edit_user(request, pk):
    if pk is None:
        return PermissionDenied
    else:
        user = User.objects.get(pk=pk)
        user_form = UserProfileForm(instance=user)

        ProfileInlineFormset = inlineformset_factory(
            User, UserProfile,
            fields=('website', 'bio', 'phone',
                    'city', 'country', 'organization', 'gender')
        )
        formset = ProfileInlineFormset(instance=user)

        if request.user.is_authenticated() and request.user.id == user.id:
            if request.method == "POST":
                user_form = UserProfileForm(
                    request.POST, request.FILES, instance=user)
                formset = ProfileInlineFormset(
                    request.POST, request.FILES, instance=user)

                if user_form.is_valid():
                    created_user = user_form.save(commit=False)
                    formset = ProfileInlineFormset(
                        request.POST, request.FILES, instance=created_user)

                    if formset.is_valid():
                        created_user.save()
                        formset.save()
                        return render(request, 'blog/post_list.html',
                                      {'posts': latest_posts,
                                       'recent': recent_posts,
                                       'messages': ['Profile Updated']})

            return render(request, "account/account_update.html", {
                "noodle": pk,
                "noodle_form": user_form,
                "formset": formset,
            })
        else:
            raise PermissionDenied


def get_user_profile(request, username):
    target = get_object_or_404(User, username=username)
    target_profile = UserProfile(user=target)
    return render(request, 'account/profile.html',
                  {'target': target, 'target_profile': target_profile,
                   'recent': recent_posts})
