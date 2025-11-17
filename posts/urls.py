from django.conf import Settings
from django.urls import path

from posts.views import PostList, like_post
from users.views import SignUpView, SignUpSuccess, Login, Profile, UpdateProfile, ProfileSettings
from django.contrib.auth import views

urlpatterns = [
    path('like/<int:pk>/', like_post, name='like_post'),

]