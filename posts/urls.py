from django.conf import Settings
from django.urls import path

from posts.views import PostList, PostCreate, like_unlike_post, add_comment, del_comment, post_delete, \
    like_unlike_comment, repost, post_detail, get_data_for_repost, PostUpdate, pag_home_posts, pag_profile_posts, \
    update_comment, user_dialogs
from users.views import SignUpView, SignUpSuccess, Login, Profile, UpdateProfile, ProfileSettings
from django.contrib.auth import views

urlpatterns = [
    path('update/<int:pk>/', PostUpdate.as_view(), name='post_update'),
    path('post_detail/<int:pk>/', post_detail, name='post_detail'),
    path('like_unlike/<int:pk>/', like_unlike_post, name='like_unlike_post'),
    path('repost/<int:pk>/', repost, name='repost'),
    path('dialogs_list/', user_dialogs, name='user_dialogs'),

    path('get_data_for_repost/<int:pk>/', get_data_for_repost, name='get_data_for_repost'),
    path('like_unlike_comment/<int:pk>/', like_unlike_comment, name='like_unlike_comment'),
    path('add_comment/<int:pk>/', add_comment, name='add_comment'),
    path('update_comment/<int:pk>/', update_comment, name='update_comment'),
    path('del_comment/<int:pk>/', del_comment, name='del_comment'),
    path('create/', PostCreate.as_view(), name='post_create'),
    path('delete/<int:pk>/', post_delete, name='post_delete'),
    path('paginate_home/', pag_home_posts, name='paginate_home_posts'),
    path('paginate_profile/<int:pk>/', pag_profile_posts, name='paginate_profile_posts'),


]