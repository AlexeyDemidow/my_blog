from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.DialogList.as_view(), name='chat_list'),
    path('dialog/<int:dialog_id>/', views.dialog_view, name='dialog'),
    path('start/<int:user_id>/', views.start_dialog, name='start_dialog'),
]