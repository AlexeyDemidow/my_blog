from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.forms import modelformset_factory, inlineformset_factory
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, UpdateView
from django.template.defaultfilters import date as django_date
from django.db.models import Exists, OuterRef, Prefetch, Count

from posts.forms import PostCreationForm, PostImageFormSet
from posts.models import Post, PostLike, Comment, PostImage, CommentLike
from users.views import Profile


class PostList(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'home.html'
    paginate_by = 3

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


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostCreationForm
    template_name = 'update_post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Исправлено: can_delete=True
        ImageFormSet = inlineformset_factory(Post, PostImage, fields=('image',), extra=50, can_delete=True)

        if self.request.POST:
            context['images_formset'] = ImageFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object
            )
        else:
            context['images_formset'] = ImageFormSet(instance=self.object)

        # Текущие изображения для шаблона
        context['post_images'] = self.object.images.all()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        images_formset = context['images_formset']

        form.instance.author = self.request.user

        if form.is_valid() and images_formset.is_valid():
            self.object = form.save()
            images_formset.instance = self.object
            images_formset.save()  # сохранение добавленных/удалённых изображений
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'pk': self.request.user.pk})


def post_detail(request, pk):
    post = (
        Post.objects
        .prefetch_related(
            'likes',                      # пост лайки
            'comments__comment_likes',    # лайки комментариев
            'comments__user',             # авторы комментариев
        )
        .get(id=pk)
    )
    comms_sort = request.GET.get('comms_sort', 'modal-date-new')
    comments = post.comments.all().annotate(likes_count=Count('comment_likes', distinct=True))

    # ---------- Сортировка ----------
    if comms_sort == 'modal-date-new':
        comments = comments.order_by('-created_at')
    elif comms_sort == 'modal-date-old':
        comments = comments.order_by('created_at')
    elif comms_sort == 'modal-likes':
        comments = comments.order_by('-likes_count', '-created_at')
    else:
        comments = comments.order_by('-created_at')


    # Если юзер не авторизован — просто помечаем флаги
    if not request.user.is_authenticated:
        post.is_liked = False
        for c in comments:
            c.is_liked = False
        return render(request, 'partials/post_modal.html', {
            'post': post,
            'comments': comments,
        })

    # ✔️ Получаем ВСЕ лайки пользователя одним запросом
    user_likes_post = post.likes.filter(user=request.user).exists()

    user_liked_comment_ids = set(
        CommentLike.objects.filter(
            user=request.user,
            comment__in=comments
        ).values_list('comment_id', flat=True)
    )

    # Проставляем флаги
    post.is_liked = user_likes_post
    for c in comments:
        c.is_liked = c.id in user_liked_comment_ids

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
        original_post=original,
        repost_text=request.POST.get("text", "")
    )
    return JsonResponse({
        'status': 'success',
        'id': new_post.id,
        'avatar': str(original.author.avatar),
        'author': new_post.author.username,
        'text': new_post.repost_text,
        'created_at': new_post.created_at.strftime('%Y-%m-%d %H:%M'),
        'orig_author': original.author.username,
        'orig_content': original.content,
        'orig_images': list(original.images.values('image'))
    })


@login_required
def get_data_for_repost(request, pk):
    post = get_object_or_404(Post, id=pk)
    images = list(post.images.values('image'))

    return JsonResponse({
        'id': post.id,
        'author': post.author.username,
        'content': post.content,
        'images': images
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
        },
        'comment_count': post.comments.count(),

    })

@require_POST
@login_required
def update_comment(request, pk):
    comment = get_object_or_404(Comment, id=pk, user=request.user)
    text = request.POST.get("text", "").strip()

    if not text:
        return JsonResponse({"status": "error"})

    comment.text = text
    comment.save()

    return JsonResponse({
        "status": "success",
        "text": comment.text
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

    return JsonResponse({
        'status': 'success',
        'comment_count': comment.post.comments.count(),
        'post_id': comment.post.id
    })


def pag_home_posts(request):
    page = request.GET.get("page", 1)
    sort = request.GET.get("sort", "date-new")

    view = PostList()
    view.request = request
    queryset = view.get_queryset()

    paginator = Paginator(queryset, 3)
    posts = paginator.get_page(page)

    html = render_to_string("partials/post_items.html", {"posts": posts, "user": request.user})

    return JsonResponse({
        "posts_html": html,
        "has_next": posts.has_next(),
        "next_page": posts.next_page_number() if posts.has_next() else None,
    })



def pag_profile_posts(request, pk):
    page = int(request.GET.get("page", 1))
    sort = request.GET.get("sort", "date-new")

    view = Profile()
    view.request = request
    view.kwargs = {"pk": pk}

    qs = view.get_posts_queryset()
    paginator = Paginator(qs, 3)
    posts = paginator.get_page(page)

    html = render_to_string(
        "partials/post_items.html",
        {"posts": posts, "user": request.user},
        request=request
    )

    return JsonResponse({
        "posts_html": html,
        "has_next": posts.has_next(),
        "next_page": posts.next_page_number() if posts.has_next() else None,
    })
