
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, DetailView, UpdateView

from posts.models import Post
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
    """Представление профиля пользователя"""

    model = CustomUser
    template_name = 'profile.html'
    context_object_name = 'customer'

    login_url = 'login'

    def get_context_data(self, **kwargs):
        sort = self.request.GET.get('sort', 'date-new')
        context = super().get_context_data(**kwargs)

        user = self.get_object()
        posts = (
            Post.objects
            .select_related('author', 'original_post', 'original_post__author')
            .prefetch_related(
                'images',
                'likes',
                'reposts',
            )
            .filter(author=self.request.user)
            .annotate(
                likes_count=Count('likes', distinct=True),
                reposts_count=Count('reposts', distinct=True),
                comments_count=Count('comments', distinct=True),
            )
        )


        if self.request.user.is_authenticated:
            for post in posts:
                post.is_liked = post.likes.filter(user=self.request.user).exists()
        else:
            for post in posts:
                post.is_liked = False

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
        context['posts'] = posts
        context['c_user'] = user
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
