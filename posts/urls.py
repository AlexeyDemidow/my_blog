from django.conf import Settings
from django.urls import path

from posts.views import PostList, PostCreate, like_unlike_post, add_comment, del_comment, post_delete, \
    like_unlike_comment, repost, post_detail
from users.views import SignUpView, SignUpSuccess, Login, Profile, UpdateProfile, ProfileSettings
from django.contrib.auth import views

urlpatterns = [
    path('post_detail/<int:pk>/', post_detail, name="post_detail"),
    path('like_unlike/<int:pk>/', like_unlike_post, name='like_unlike_post'),
    path('repost/<int:pk>/', repost, name='repost'),
    path('like_unlike_comment/<int:pk>/', like_unlike_comment, name='like_unlike_comment'),
    path('add_comment/<int:pk>/', add_comment, name='add_comment'),
    path('del_comment/<int:pk>/', del_comment, name='del_comment'),
    path('create/', PostCreate.as_view(), name='post_create'),
    path('delete/<int:pk>/', post_delete, name='post_delete'),

]