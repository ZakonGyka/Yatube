from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Group, Post, User, Follow


# @cache_page(20)
# кэширование через view
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 15)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group,
                                          'page': page,
                                          'paginator': paginator
                                          }
                  )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list_author = author.posts.all()
    paginator = Paginator(post_list_author, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = request.user.is_authenticated and Follow.objects.filter(author=author, user=request.user).exists()
    follower_count = Follow.objects.filter(author=author).count()
    following_count = Follow.objects.filter(user=author).count()
    return render(request, 'profile.html',
                  {'author': author,
                   'page': page,
                   'paginator': paginator,
                   'following': following,
                   'following_count': following_count,
                   'follower_count': follower_count,
                   }
                  )


def post_concrete_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm()
    if request.user.is_authenticated:
        following = Follow.objects.filter(author=author, user=request.user).exists()
        return render(request, 'post_concrete.html',
                      {
                          'user': request.user,
                          'post': post,
                          'form': form,
                          'following': following,
                      }
                      )
    return render(request, 'post_concrete.html',
                  {
                      'user': request.user,
                      'post': post,
                      'form': form,
                  }
                  )


@login_required(login_url='/auth/login/')
def new_post(request):
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None, )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(reverse('index'))
    return render(request,
                  'post_new_or_edit.html',
                  {'form': form,
                   'create_post': True,
                   }
                  )


@login_required(login_url='/auth/login/')
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    login_user = request.user
    if login_user != post.author:
        return redirect(reverse('post_concrete',
                                kwargs={
                                    'username': post.author.username,
                                    'post_id': post_id,
                                }
                                )
                        )
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        post.save()
        return redirect(reverse('post_concrete',
                                kwargs={
                                    'username': post.author.username,
                                    'post_id': post_id,
                                }
                                )
                        )
    return render(request, 'post_new_or_edit.html',
                  {'form': form,
                   'post': post,
                   'create_post': False,
                   }
                  )


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required(login_url='/auth/login/')
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if request.method != "POST":
        return redirect(reverse('post_concrete', kwargs={'username': username, 'post_id': post_id}))
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect(reverse('post_concrete', kwargs={'username': username, 'post_id': post_id}))


@login_required
def follow_index(request):
    following_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(following_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page, 'paginator': paginator, 'following_list': following_list})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        if not Follow.objects.filter(user=request.user, author=author):
            Follow.objects.create(user=request.user, author=author)
    return redirect("profile", username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if Follow.objects.filter(user=request.user, author=author):
        Follow.objects.get(user=request.user, author=author).delete()
    return redirect("profile", username)
