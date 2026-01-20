from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db.models import Count, Exists, OuterRef, Value
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, TemplateView, DetailView, UpdateView, ListView

from posts.models import Post, PostLike
from users.forms import CustomUserCreationForm
from users.models import CustomUser, UserFollow


class SignUpView(CreateView):
    """Представление регистрации пользователя"""

    model = CustomUser
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('signup_success')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class SignUpSuccess(TemplateView):
    """Представление успешной регистрации пользователя"""

    template_name = 'registration/signup_success.html'


class Login(LoginView):
    """Представление входа в систему"""

    form_class = AuthenticationForm
    template_name = 'login.html'
    success_url = reverse_lazy('home')


class Profile(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'profile.html'
    context_object_name = 'customer'
    login_url = 'login'

    def get_posts_queryset(self):
        user = self.get_object()
        sort = self.request.GET.get('sort', 'date-new')

        qs = (
            Post.objects
            .filter(author=user)
            .annotate(
                likes_count=Count('likes', distinct=True),
                reposts_count=Count('reposts', distinct=True),
                comments_count=Count('comments', distinct=True),
                is_liked=Exists(
                    PostLike.objects.filter(
                        post=OuterRef('pk'),
                        user=self.request.user
                    )
                ) if self.request.user.is_authenticated else Value(False)
            )
            .select_related('author', 'original_post', 'original_post__author')
            .prefetch_related('images', 'likes', 'reposts')
        )

        if sort == 'date-new':
            qs = qs.order_by('-created_at')
        elif sort == 'date-old':
            qs = qs.order_by('created_at')
        elif sort == 'likes':
            qs = qs.order_by('-likes_count', '-created_at')
        elif sort == 'reposts':
            qs = qs.order_by('-reposts_count', '-created_at')
        elif sort == 'comments':
            qs = qs.order_by('-comments_count', '-created_at')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        is_following = False
        if self.request.user.is_authenticated and self.request.user != user:
            is_following = UserFollow.objects.filter(
                follower=self.request.user,
                following=user
            ).exists()

        qs = self.get_posts_queryset()
        paginator = Paginator(qs, 3)
        page = self.request.GET.get("page", 1)
        posts = paginator.get_page(page)

        context["posts"] = posts
        context["c_user"] = self.get_object()
        context["has_next"] = posts.has_next()
        context["is_following"] = is_following

        return context


class ProfileSettings(TemplateView):

    template_name = 'settings.html'


class UpdateProfile(LoginRequiredMixin, UpdateView):

    model = CustomUser
    fields = ['username', 'email', 'avatar', 'bio']
    template_name = 'update_profile.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('profile', kwargs={'pk': pk})


class ProfileSearch(LoginRequiredMixin, ListView):
    model = CustomUser
    context_object_name = 'profiles'
    template_name = 'search.html'


def profile_search(request):

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        res = None
        profile_name = request.POST.get('profile_name').capitalize()
        querry = CustomUser.objects.filter(username__icontains=profile_name)
        if len(querry) > 0 and len(profile_name) > 0:
            data = []
            for prof in querry:
                profile_view = {
                    'id': prof.id,
                    'username': prof.username,
                    'bio': prof.bio,
                    'pic': str(prof.avatar.url)
                }
                data.append(profile_view)
            res = data
        else:
            res = 'Ничего не найдено'
        return JsonResponse({'data': res})
    return JsonResponse({})


@login_required
@require_POST
def toggle_follow(request, pk):
    target = get_object_or_404(CustomUser, id=pk)

    if target == request.user:
        return JsonResponse({'error': 'self_follow'}, status=400)

    follow, created = UserFollow.objects.get_or_create(
        follower=request.user,
        following=target
    )

    if not created:
        follow.delete()
        is_following = False
    else:
        is_following = True

    return JsonResponse({
        'is_following': is_following,
        'followers_count': target.followers.count()
    })

class Subscriptions(LoginRequiredMixin, ListView):
    model = UserFollow
    context_object_name = 'subscriptions'
    template_name = 'subscriptions.html'

    def get_queryset(self):
        return UserFollow.objects.filter(follower=self.request.user)


class Subscribers(LoginRequiredMixin, ListView):
    model = UserFollow
    context_object_name = 'subscribers'
    template_name = 'subscribers.html'

    def get_queryset(self):
        return CustomUser.objects.filter(following__following=self.request.user)


def subscribers_search(request, pk):

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        res = None
        profile_name = request.POST.get('profile_name').capitalize()
        querry = CustomUser.objects.filter(following__following=request.user, username__icontains=profile_name)
        if len(querry) > 0 and len(profile_name) >= 0:
            data = []
            for prof in querry:
                profile_view = {
                    'id': prof.id,
                    'username': prof.username,
                    'bio': prof.bio,
                    'pic': str(prof.avatar.url)
                }
                data.append(profile_view)
            res = data
        else:
            res = 'Ничего не найдено'
        return JsonResponse({'data': res})
    return JsonResponse({})


def subscriptions_search(request, pk):

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        res = None
        profile_name = request.POST.get('profile_name').capitalize()
        querry = UserFollow.objects.filter(follower=request.user, following__username__icontains=profile_name)
        if len(querry) > 0 and len(profile_name) >= 0:
            data = []
            for prof in querry:
                profile_view = {
                    'id': prof.id,
                    'username': prof.following.username,
                    'bio': prof.following.bio,
                    'pic': str(prof.following.avatar.url)
                }
                data.append(profile_view)
            res = data
        else:
            res = 'Ничего не найдено'
        return JsonResponse({'data': res})
    return JsonResponse({})