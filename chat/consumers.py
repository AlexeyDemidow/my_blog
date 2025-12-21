import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache


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

        # if data.get('type') == 'read_all':
        #     await self.mark_messages_as_read()
        #     await self.channel_layer.group_send(
        #         self.room_group_name,
        #         {
        #             'type': 'messages_read',
        #             'reader': self.scope['user'].username
        #         }
        #     )
        #     return

        if data.get('type') == 'read_all':
            await self.mark_messages_as_read()

            dialog_users = await self.get_dialog_users()

            for user_id in dialog_users:
                if user_id != self.scope['user'].id:
                    # 🔹 1. В ОТКРЫТЫЙ ДИАЛОГ
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'messages_read',
                        }
                    )

                    # 🔹 2. В СПИСОК ЧАТОВ
                    await self.channel_layer.group_send(
                        f'user_{user_id}',
                        {
                            'type': 'messages_read',
                            'dialog_id': self.dialog_id
                        }
                    )

            return

        dialog_users = await self.get_dialog_users()

        for user_id in dialog_users:
            if user_id != self.scope['user'].id:
                await self.channel_layer.group_send(
                    f'user_{user_id}',
                    {
                        'type': 'messages_read',
                        'dialog_id': self.dialog_id
                    }
                )

        # 🔔 typing
        if data.get('type') == 'typing':
            await self.handle_typing(data)
            return

        # ✉️ обычное сообщение
        message_text = data.get('message', '').strip()
        if not message_text:
            return

        user = self.scope['user']

        message = await self.save_message(user.id, message_text)

        # уведомляем второго участника
        dialog_users = await self.get_dialog_users()

        for user_id in dialog_users:
            if user_id != user.id:
                await self.channel_layer.group_send(
                    f'user_{user_id}',
                    {
                        'type': 'new_message',
                        'dialog_id': self.dialog_id,
                        'message': message.text,
                        'sender': user.username,
                        'from_me': False
                    }
                )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'id': message.id,
                'message': message.text,
                'sender': user.username,
                'sender_id': user.id,
                'is_read': False,
            }
        )

    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'username': event['username'],
            'is_typing': event['is_typing'],
        }))

    # async def chat_message(self, event):
    #     # Отправка сообщения клиенту
    #     await self.send(text_data=json.dumps(event))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

        # 🔥 если сообщение пришло НЕ от меня — читаем сразу
        if event.get('sender_id') != self.scope['user'].id:
            # отмечаем сообщение прочитанным
            await self.mark_message_read(event['id'])

            # уведомляем отправителя
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'messages_read',
                }
            )

            # и список чатов
            await self.channel_layer.group_send(
                f'user_{event["sender_id"]}',
                {
                    'type': 'messages_read',
                    'dialog_id': self.dialog_id
                }
            )

    async def messages_read(self, event):
        await self.send(text_data=json.dumps(event))

    async def chat_typing(self, event):
        await self.send(text_data=json.dumps(event))

    async def handle_typing(self, data):
        username = self.scope['user'].username
        is_typing = data.get('is_typing', False)

        # typing в диалоге
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_typing',
                'username': username,
                'is_typing': is_typing,
            }
        )

        # typing в списке бесед
        dialog_users = await self.get_dialog_users()

        for user_id in dialog_users:
            if user_id != self.scope['user'].id:
                await self.channel_layer.group_send(
                    f'user_{user_id}',
                    {
                        'type': 'chat_typing',
                        'dialog_id': self.dialog_id,
                        'username': username,
                        'is_typing': is_typing
                    }
                )

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

    @database_sync_to_async
    def mark_message_read(self, message_id):
        from .models import Message
        Message.objects.filter(id=message_id).update(is_read=True)

    @database_sync_to_async
    def get_dialog_users(self):
        from .models import Dialog
        dialog = Dialog.objects.get(id=self.dialog_id)
        return list(dialog.users.values_list('id', flat=True))


class ChatListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
            return

        self.group_name = f'user_{user.id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name)

    # async def chat_notification(self, event):
    #     await self.send(text_data=json.dumps(event))

    async def chat_typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_typing',
            'dialog_id': event['dialog_id'],
            'username': event['username'],
            'is_typing': event['is_typing']
        }))

    async def new_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'dialog_id': event['dialog_id'],
            'message': event['message'],
            'sender': event['sender'],
            'from_me': False
        }))

    # async def messages_read_list(self, event):
    #     await self.send(text_data=json.dumps({
    #         'type': 'messages_read',
    #         'dialog_id': event['dialog_id']
    #     }))

    async def messages_read(self, event):
        await self.send(text_data=json.dumps({
            'type': 'messages_read',
            'dialog_id': event['dialog_id']
        }))


ONLINE_USERS_KEY = 'online_users'

class OnlineStatusConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
            return

        self.user = user
        self.group_name = 'online_users'
        self.cache_key = f'online_count_{user.id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

        # ⬇счётчик подключений
        count = cache.get(self.cache_key, 0) + 1
        cache.set(self.cache_key, count)

        # ⬇️ если первое подключение
        if count == 1:
            online_users = set(cache.get(ONLINE_USERS_KEY, []))
            online_users.add(user.id)
            cache.set(ONLINE_USERS_KEY, list(online_users))

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'user_online',
                    'user_id': user.id,
                }
            )

        # отправляем текущий online-список НОВОМУ клиенту
        await self.send(text_data=json.dumps({
            'type': 'online_users',
            'users': cache.get(ONLINE_USERS_KEY, [])
        }))

    async def disconnect(self, close_code):
        count = cache.get(self.cache_key, 1) - 1

        if count <= 0:
            cache.delete(self.cache_key)

            online_users = set(cache.get(ONLINE_USERS_KEY, []))
            online_users.discard(self.user.id)
            cache.set(ONLINE_USERS_KEY, list(online_users))

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'user_offline',
                    'user_id': self.user.id,
                }
            )
        else:
            cache.set(self.cache_key, count)

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def user_online(self, event):
        await self.send(text_data=json.dumps(event))

    async def user_offline(self, event):
        await self.send(text_data=json.dumps(event))