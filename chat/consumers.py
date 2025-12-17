import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.dialog_id = self.scope['url_route']['kwargs']['dialog_id']
        self.room_group_name = f'dialog_{self.dialog_id}'

        # Проверяем, имеет ли пользователь доступ к диалогу
        if not await self.user_has_access():
            await self.close()
            return

        # Подключаемся к группе WebSocket
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Отключаемся от группы WebSocket
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get('type') == 'read_all':
            await self.mark_messages_as_read()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'messages_read',
                    'reader': self.scope['user'].username
                }
            )
            return

        # 🔔 typing indicator
        if data.get('type') == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_typing',
                    'username': self.scope['user'].username,
                    'is_typing': data.get('is_typing', False),
                }
            )
            return

        # ✉️ обычное сообщение
        message_text = data.get('message', '').strip()
        if not message_text:
            return

        user = self.scope['user']

        message = await self.save_message(user.id, message_text)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'id': message.id,
                'message': message.text,
                'sender': user.username,
                'is_read': False,
            }
        )

    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'username': event['username'],
            'is_typing': event['is_typing'],
        }))

    async def chat_message(self, event):
        # Отправка сообщения клиенту
        await self.send(text_data=json.dumps(event))

    async def messages_read(self, event):
        await self.send(text_data=json.dumps(event))

    # ---------------------------
    # Работа с базой данных
    # ---------------------------

    @database_sync_to_async
    def save_message(self, user_id, text):
        # Ленивый импорт моделей, чтобы избежать ошибок Apps aren't loaded yet
        from .models import Dialog, Message

        dialog = Dialog.objects.get(id=self.dialog_id)
        return Message.objects.create(
            dialog=dialog,
            sender_id=user_id,
            text=text
        )

    @database_sync_to_async
    def user_has_access(self):
        from .models import Dialog

        dialog = Dialog.objects.filter(id=self.dialog_id).first()
        if not dialog:
            return False

        # Сравниваем по id, чтобы избежать ленивых ссылок
        return self.scope['user'].id in [u.id for u in dialog.users.all()]

    @database_sync_to_async
    def mark_messages_as_read(self):
        from .models import Message
        Message.objects.filter(
            dialog_id=self.dialog_id,
            is_read=False
        ).exclude(sender=self.scope['user']).update(is_read=True)

