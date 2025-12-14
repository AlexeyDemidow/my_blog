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
        # Получаем сообщение от клиента
        data = json.loads(text_data)
        message_text = data.get('message', '').strip()
        if not message_text:
            return

        user = self.scope['user']

        # Сохраняем сообщение в базе
        message = await self.save_message(user.id, message_text)

        # Отправляем сообщение всем в группе
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message.text,
                'sender': user.username,
                'created_at': message.created_at.isoformat(),
            }
        )

    async def chat_message(self, event):
        # Отправка сообщения клиенту
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
