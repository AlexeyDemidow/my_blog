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
        return Post.objects.all()


@login_required
def like_post(request, pk):
    """Представление для AJAX-запроса добавления товара в корзину и увеличения количества в корзине"""
    post = get_object_or_404(Post, id=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    # if like:
    #     like.save()

    return JsonResponse({'status': 'success'})


# @login_required
# def unlike_post(request, pk):
#     """Представление для AJAX-запроса добавления товара в корзину и увеличения количества в корзине"""
#     post = get_object_or_404(Post, id=pk)
#     like, created = Like.objects.get_or_create(user=request.user, post=post)
#
#     if like:
#         like.delete()
#
#     return JsonResponse({'status': 'success'})