from django.urls import path
from django.contrib.auth import views

from users.views import *

urlpatterns = [
    path('<int:pk>/', Profile.as_view(), name='profile'),
    path('settings/', ProfileSettings.as_view(), name='settings'),
    path('<int:pk>/update_profile/', UpdateProfile.as_view(), name='update_profile'),
    path('<int:pk>/follow/', toggle_follow, name='toggle_follow'),
    path('signup/', SignUpView.as_view(), name='account_signup'),
    path('login/', Login.as_view(), name='account_login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('search/', ProfileSearch.as_view(), name='profile_search'),
    path('search/search_result/', profile_search, name='profile_search_result'),
    path('<int:pk>/subscribers/subscribers_search_result/', subscribers_search, name='subscribers_search_result'),
    path('<int:pk>/subscriptions/subscriptions_search_result/', subscriptions_search, name='subscriptions_search_result'),
    path('<int:pk>/subscriptions/', Subscriptions.as_view(), name='subscriptions'),
    path('<int:pk>/subscribers/', Subscribers.as_view(), name='subscribers'),

]
