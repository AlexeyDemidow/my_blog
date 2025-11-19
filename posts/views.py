from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django.template.defaultfilters import date as django_date

from posts.models import Post, Like, Comment


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


@require_POST
@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, id=pk)
    text = request.POST.get('text', '').strip()
    if not text:
        return HttpResponseBadRequest('Empty comment')

    # создаём новый комментарий
    comment = Comment.objects.create(
        user=request.user,
        post=post,
        text=text,
        created_at=timezone.now()
    )

    return JsonResponse({
        'status': 'success',
        'comment': {
            'id': comment.id,
            'text': comment.text,
            'user': request.user.username,
            'created_at': django_date(comment.created_at, "d E Y г. H:i"),
        }
    })

