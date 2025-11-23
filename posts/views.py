from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView
from django.template.defaultfilters import date as django_date

from posts.forms import PostCreationForm, PostImageFormSet
from posts.models import Post, Like, Comment, PostImage


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


class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostCreationForm
    template_name = 'create_post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['images_formset'] = PostImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['images_formset'] = PostImageFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        images_formset = context['images_formset']

        # Создаем пост
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()

        # Сохраняем изображения
        if images_formset.is_valid():
            for image_form in images_formset:
                if image_form.cleaned_data.get('image'):
                    PostImage.objects.create(post=post, image=image_form.cleaned_data['image'])
        return super().form_valid(form)

    def get_success_url(self):
        pk = self.request.user.pk
        return reverse_lazy('profile', kwargs={'pk': pk})


@require_POST
@login_required
def post_delete(request, pk):
    # post = Post.objects.filter(id=pk).first()
    post = get_object_or_404(Post, id=pk)
    if not post:
        return JsonResponse({'status': 'error', 'message': 'not found or forbidden'}, status=403)

    post.delete()

    return JsonResponse({'status': 'success'})


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
            'is_owner': comment.user == request.user,
        }
    })

@require_POST
@login_required
def del_comment(request, pk):
    comment = Comment.objects.filter(
        id=pk,
        user=request.user
    ).first()

    if not comment:
        return JsonResponse({'status': 'error', 'message': 'not found or forbidden'}, status=403)

    comment.delete()

    return JsonResponse({'status': 'success'})