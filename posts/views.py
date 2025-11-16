from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView

from posts.models import Post


class PostList(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'home.html'

    def get_queryset(self):
        print(Post.objects.all())
        return Post.objects.all()

