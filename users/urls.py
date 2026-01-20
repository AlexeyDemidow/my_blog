from django.conf import Settings
from django.urls import path

from users.views import SignUpView, SignUpSuccess, Login, Profile, UpdateProfile, ProfileSettings, ProfileSearch, \
    profile_search, toggle_follow, Subscriptions, Subscribers, subscribers_search, subscriptions_search
from django.contrib.auth import views

urlpatterns = [
    path('<int:pk>/', Profile.as_view(), name='profile'),  # Профиль
    path('settings/', ProfileSettings.as_view(), name='settings'),
    path('<int:pk>/update_profile/', UpdateProfile.as_view(), name='update_profile'),  # Обновление данных профиля
    path('<int:pk>/follow/', toggle_follow, name='toggle_follow'),
    path('signup/', SignUpView.as_view(), name='signup'),  # Регистрация
    path('signup_success/', SignUpSuccess.as_view(), name='signup_success'),  # Сигнал об успешной регистрации
    path('login/', Login.as_view(), name='login'),  # Вход
    path('logout/', views.LogoutView.as_view(), name='logout'),  # Выход
    path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),  # Сброс пароля
    path('password_reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),  # Сигнал об успешном сбросе пароля
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),  # Подтверждение сброса пароля
    path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),  # Сброс пароля успешен
    path('search/', ProfileSearch.as_view(), name='profile_search'),
    path('search/search_result/', profile_search, name='profile_search_result'),
    path('<int:pk>/subscribers/subscribers_search_result/', subscribers_search, name='subscribers_search_result'),
    path('<int:pk>/subscriptions/subscriptions_search_result/', subscriptions_search, name='subscriptions_search_result'),
    path('<int:pk>/subscriptions/', Subscriptions.as_view(), name='subscriptions'),
    path('<int:pk>/subscribers/', Subscribers.as_view(), name='subscribers'),

]