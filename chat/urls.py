from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.DialogList.as_view(), name='chat_list'),
    path('dialog/<int:dialog_id>/', views.dialog_view, name='dialog'),
    path('start/<int:user_id>/', views.start_dialog, name='start_dialog'),
    path('dialog/<int:dialog_id>/pin/', views.toggle_pin, name='toggle_pin'),
    path('dialog/<int:dialog_id>/messages/<int:message_id>/pin/', views.toggle_message_pin, name='toggle_message_pin'),
    path('like_unlike_message/<int:message_id>/', views.like_unlike_message, name='like_unlike_message'),
    path('dialog/<int:dialog_id>/messages/', views.pag_messages, name='pag_messages'),


]