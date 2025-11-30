from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import modelformset_factory, inlineformset_factory
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView
from django.template.defaultfilters import date as django_date
from django.db.models import Exists, OuterRef, Prefetch, Count

from posts.forms import PostCreationForm, PostImageFormSet
from posts.models import Post, PostLike, Comment, PostImage, CommentLike


class PostList(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'home.html'

    def get_queryset(self):
        sort = self.request.GET.get('sort', 'date-new')

        # Базовый queryset с предзагрузкой связей
        posts = (
            Post.objects
            .select_related('author', 'original_post', 'original_post__author')
            .prefetch_related(
                'images',
                'likes',
                'reposts',
            )
            .annotate(
                likes_count=Count('likes', distinct=True),
                reposts_count=Count('reposts', distinct=True),
                comments_count=Count('comments', distinct=True),
            )
        )

        if self.request.user.is_authenticated:
            # Предзагружаем комментарии с аннотацией is_liked и лайками
            comments_queryset = Comment.objects.select_related('user').annotate(
                is_liked=Exists(
                    CommentLike.objects.filter(user=self.request.user, comment=OuterRef('pk'))
                )
            ).prefetch_related('comment_likes')

            posts = posts.prefetch_related(
                Prefetch('comments', queryset=comments_queryset)
            ).annotate(
                is_liked=Exists(
                    PostLike.objects.filter(user=self.request.user, post=OuterRef('pk'))
                )
            )
        else:
            # Анонимному пользователю просто предзагружаем комментарии
            posts = posts.prefetch_related('comments')

        # ---------- Сортировка ----------
        if sort == 'date-new':
            posts = posts.order_by('-created_at')
        elif sort == 'date-old':
            posts = posts.order_by('created_at')
        elif sort == 'likes':
            posts = posts.order_by('-likes_count', '-created_at')
        elif sort == 'reposts':
            posts = posts.order_by('-reposts_count', '-created_at')
        elif sort == 'comments':
            posts = posts.order_by('-comments_count', '-created_at')
        else:
            posts = posts.order_by('-created_at')

        return posts


class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostCreationForm
    template_name = 'create_post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ImageFormSet = inlineformset_factory(Post, PostImage, fields=('image',), extra=50, can_delete_extra=True)
        if self.request.POST:
            context['images_formset'] = ImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['images_formset'] = ImageFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        images_formset = context['images_formset']

        # Присваиваем автора
        form.instance.author = self.request.user

        if form.is_valid() and images_formset.is_valid():
            self.object = form.save()  # Сохраняем пост
            images_formset.instance = self.object
            images_formset.save()  # Сохраняем изображения
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'pk': self.request.user.pk})


def post_detail(request, pk):
    post = get_object_or_404(Post, id=pk)
    comments = post.comments.all().order_by('-created_at')
    return render(request, 'partials/post_modal.html', {
        'post': post,
        'comments': comments,
    })



@require_POST
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, id=pk, author=request.user)

    # Проверяем, является ли пост репостом
    original_post_id = None
    if post.original_post:
        original_post_id = post.original_post.id

    post.delete()

    return JsonResponse({
        'status': 'success',
        'original_post_id': original_post_id
    })


@login_required
def like_unlike_post(request, pk):
    post = get_object_or_404(Post, id=pk)

    like, created = PostLike.objects.get_or_create(user=request.user, post=post)
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


@login_required
def repost(request, pk):
    original = get_object_or_404(Post, id=pk)

    # Проверяем, не репостил ли уже пользователь этот пост
    existing = Post.objects.filter(
        author=request.user,
        original_post=original
    ).first()

    if existing:
        return JsonResponse({
            'status': 'error',
            'message': 'Вы уже репостили этот пост'
        })

    new_post = Post.objects.create(
        author=request.user,
        original_post=original
    )

    return JsonResponse({
        'status': 'success',
        'post_id': new_post.id
    })



@login_required
def like_unlike_comment(request, pk):
    comment = get_object_or_404(Comment, id=pk)

    comment_like, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)
    if not created:
        comment_like.delete()
        is_liked = False
    else:
        is_liked = True

    return JsonResponse({
        'status': 'success',
        'is_liked': is_liked,
        'like_count': comment.comment_likes.count()
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
    print(comment.comment_likes.exists())
    return JsonResponse({
        'status': 'success',
        'comment': {
            'id': comment.id,
            'text': comment.text,
            'user': request.user.username,
            'created_at': django_date(comment.created_at, "d E Y г. H:i"),
            'is_owner': comment.user == request.user,
            'like_count': comment.comment_likes.count(),
            'is_liked': comment.comment_likes.exists()
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