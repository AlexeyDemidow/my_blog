from django.urls import path
from .consumers import PrivateChatConsumer, ChatListConsumer, OnlineStatusConsumer

websocket_urlpatterns = [
    path('ws/chat/<int:dialog_id>/', PrivateChatConsumer.as_asgi()),
    path('ws/chat_list/', ChatListConsumer.as_asgi()),
    path('ws/online/', OnlineStatusConsumer.as_asgi()),
]
