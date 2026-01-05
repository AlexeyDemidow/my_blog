
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db.models import Count, Exists, OuterRef, Value
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, DetailView, UpdateView

from posts.models import Post, PostLike
from users.forms import CustomUserCreationForm
from users.models import CustomUser


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

        qs = self.get_posts_queryset()
        paginator = Paginator(qs, 3)
        page = self.request.GET.get("page", 1)
        posts = paginator.get_page(page)

        context["posts"] = posts
        context["c_user"] = self.get_object()
        context["has_next"] = posts.has_next()

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
