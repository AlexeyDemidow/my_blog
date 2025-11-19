from django.conf import Settings
from django.urls import path

from posts.views import PostList, like_unlike_post, add_comment
from users.views import SignUpView, SignUpSuccess, Login, Profile, UpdateProfile, ProfileSettings
from django.contrib.auth import views

urlpatterns = [
    path('like_unlike/<int:pk>/', like_unlike_post, name='like_unlike_post'),
    path('add_comment/<int:pk>/', add_comment, name='add_comment'),

]