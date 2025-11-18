from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

from posts.models import Post, Like


class PostList(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'home.html'

    def get_queryset(self):
        posts = Post.objects.all()

        if self.request.user.is_authenticated:  # Проверка на наличие лайка
            for post in posts:
                post.is_liked = post.likes.filter(user=self.request.user).exists()

        return posts


@login_required
def like_unlike_post(request, pk):
    post = get_object_or_404(Post, id=pk)

    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        is_liked = False
    else:
        is_liked = True

    return JsonResponse({
        'status': 'success',
        'is_liked': is_liked,
        'like_count': post.likes.count()
    })
