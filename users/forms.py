
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *
from django.forms import ModelForm
from datetime import datetime


class CustomUserCreationForm(UserCreationForm):
    """Форма создания пользователя"""

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'bio', 'avatar']


class CustomUserChangeForm(UserChangeForm):
    """Форма изменения данных пользователя"""

    password = None

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'bio', 'avatar']


class CustomUserChangeFormAdmin(UserChangeForm):
    """Форма изменения данных пользователя в админ-панели"""

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'bio', 'avatar']



