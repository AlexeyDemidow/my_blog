from django.conf import Settings
from django.urls import path

from posts.views import PostList
from users.views import SignUpView, SignUpSuccess, Login, Profile, UpdateProfile, ProfileSettings
from django.contrib.auth import views

urlpatterns = [


]