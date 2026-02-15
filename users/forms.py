from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'bio', 'avatar']


class CustomUserChangeForm(UserChangeForm):

    password = None

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'bio', 'avatar']


class CustomUserChangeFormAdmin(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'bio', 'avatar']
