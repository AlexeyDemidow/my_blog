
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, DetailView, UpdateView

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
    success_url_allowed_hosts = reverse_lazy('home')
    template_name = 'login.html'


class Profile(LoginRequiredMixin, DetailView):
    """Представление профиля пользователя"""

    model = CustomUser
    template_name = 'profile.html'
    context_object_name = 'customer'

    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.get_object()
        posts = user.post_set.all()

        if self.request.user.is_authenticated:
            for post in posts:
                post.is_liked = post.likes.filter(user=self.request.user).exists()
        else:
            for post in posts:
                post.is_liked = False

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
