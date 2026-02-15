import json

from django.core.cache import cache
from django.utils import timezone
from django.utils.formats import date_format

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from chat.models import Message, MessageLike


class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.dialog_id = self.scope['url_route']['kwargs']['dialog_id']
        self.room_group_name = f'dialog_{self.dialog_id}'

        if not await self.user_has_access():
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data['type'] == 'toggle_like':
            await self.toggle_like(data['message_id'])

        if data.get('type') == 'messages_read':
            read_ids = await self.mark_messages_as_read()
            if not read_ids:
                return

            for user_id in await self.get_dialog_users():
                if user_id != self.scope['user'].id:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'messages_read',
                            'dialog_id': self.dialog_id,
                            'message_ids': read_ids
                        }
                    )
            return

        if data["type"] == "edit_message":
            await self.edit_message(data)
            return

        if data.get('type') == 'typing':
            await self.handle_typing(data)
            return

        if data["type"] == "delete_message":
            await self.delete_message(data)
            return

        message_text = data.get('message', '').strip()
        if not message_text:
            return

        user = self.scope['user']
        message = await self.save_message(user.id, message_text)

        for user_id in await self.get_dialog_users():
            if user_id != user.id:
                was_hidden = await self.unhide_dialog_for_user(user_id)

                await self.channel_layer.group_send(
                    f'user_{user_id}',
                    {
                        'type': 'new_message',
                        'dialog_id': self.dialog_id,
                        'message': message.text,
                        'message_created_at': date_format(message.created_at, "j E Y г. H:i"),
                        'sender': user.username,
                        'from_me': False,
                        'unhide': was_hidden
                    }
                )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'id': message.id,
                'message': message.text,
                'message_created_at': date_format(message.created_at, "j E Y г. H:i"),
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

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def messages_read(self, event):
        await self.send(text_data=json.dumps(event))

    async def toggle_like(self, message_id):
        data = await self.toggle_like_db(message_id)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'like_update',
                **data
            }
        )

    async def like_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'like_update',
            'message_id': event['message_id'],
            'is_liked': event['is_liked'],
            'like_count': event['like_count'],
            'username': event['username'],
        }))

    async def chat_typing(self, event):
        await self.send(text_data=json.dumps(event))

    async def handle_typing(self, data):
        username = self.scope['user'].username
        is_typing = data.get('is_typing', False)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_typing',
                'username': username,
                'is_typing': is_typing,
            }
        )

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

    async def edit_message(self, data):
        message_id = data.get("message_id")
        new_text = data.get("text", "").strip()
        user = self.scope["user"]

        if not new_text:
            return

        from chat.models import Message

        try:
            message = await database_sync_to_async(Message.objects.get)(id=message_id, sender=user)
        except Message.DoesNotExist:
            return

        message.text = new_text
        message.is_edited = True
        await database_sync_to_async(message.save)()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "message_edited",
                "message_id": message.id,
                "text": message.text,
                "username": user.username,
                "created_at": date_format(message.created_at, "j E Y г. H:i"),
                "is_read": message.is_read,
            }
        )

    async def message_edited(self, event):
        await self.send(text_data=json.dumps({
            "type": "message_edited",
            "message_id": event["message_id"],
            "text": event["text"],
            "username": event["username"],
            "created_at": event["created_at"],
            "is_read": event["is_read"],
        }))

    async def delete_message(self, data):
        message_id = data.get("message_id")
        user = self.scope["user"]

        from chat.models import Message

        try:
            message = await database_sync_to_async(Message.objects.get)(id=message_id, sender=user)
        except Message.DoesNotExist:
            return

        await database_sync_to_async(message.delete)()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "message_deleted",
                "message_id": message_id
            }
        )

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({
            "type": "message_deleted",
            "message_id": event["message_id"]
        }))

    @database_sync_to_async
    def save_message(self, user_id, text):
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

        return self.scope['user'].id in [u.id for u in dialog.users.all()]

    @database_sync_to_async
    def mark_messages_as_read(self):
        from .models import Message
        qs = Message.objects.filter(
            dialog_id=self.dialog_id,
            is_read=False
        ).exclude(sender=self.scope['user'])

        ids = list(qs.values_list('id', flat=True))
        qs.update(is_read=True)
        return ids

    @database_sync_to_async
    def mark_message_read(self, message_id):
        from .models import Message
        Message.objects.filter(id=message_id).update(is_read=True)

    @database_sync_to_async
    def get_dialog_users(self):
        from .models import Dialog
        dialog = Dialog.objects.get(id=self.dialog_id)
        return list(dialog.users.values_list('id', flat=True))

    @database_sync_to_async
    def toggle_like_db(self, message_id):
        message = Message.objects.get(id=message_id)
        user = self.scope['user']
        like, created = MessageLike.objects.get_or_create(
            message=message,
            sender=self.scope['user']
        )
        if not created:
            like.delete()
            is_liked = False
        else:
            is_liked = True

        return {
            'message_id': message_id,
            'is_liked': is_liked,
            'like_count': message.message_likes.count(),
            'username': user.username
        }

    @database_sync_to_async
    def unhide_dialog_for_user(self, user_id):
        from chat.models import DialogUser
        dialog_user = DialogUser.objects.filter(dialog_id=self.dialog_id, user_id=user_id).first()
        if dialog_user and dialog_user.is_hidden:
            dialog_user.is_hidden = False
            dialog_user.hidden_at = None
            dialog_user.save()
            return True
        return False


class ChatListConsumer(AsyncWebsocketConsumer):
    group_name = None

    async def receive(self, text_data):
        data = json.loads(text_data)
        dialog_id = data.get('dialog_id')

        if data['type'] == 'delete_dialog_me':
            await self.hide_dialog(data['dialog_id'])

        if data['type'] == 'delete_dialog_all':
            await self.delete_dialog_all(data['dialog_id'])


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


    async def chat_deleted(self, event):
        await self.send(text_data=json.dumps({
            "type": "dialog_deleted",
            'dialog_id': event['dialog_id'],
        }))

    async def hide_dialog(self, dialog_id):
        from chat.models import DialogUser

        user = self.scope['user']

        dialog_user = await database_sync_to_async(
            lambda: DialogUser.objects.filter(dialog_id=dialog_id, user=user).first()
        )()

        if not dialog_user:
            return

        dialog_user.is_hidden = True
        dialog_user.hidden_at = timezone.now()
        await database_sync_to_async(dialog_user.save)()

        await self.send(text_data=json.dumps({
            'type': 'dialog_hidden',
            'dialog_id': dialog_id
        }))

    async def dialog_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'dialog_deleted',
            'dialog_id': event['dialog_id']
        }))

    async def delete_dialog_all(self, dialog_id):
        from chat.models import Dialog

        user = self.scope['user']

        dialog = await database_sync_to_async(
            Dialog.objects.filter(id=dialog_id, users=user).first
        )()

        if not dialog:
            return

        users = await database_sync_to_async(
            lambda: list(dialog.users.values_list('id', flat=True))
        )()

        await database_sync_to_async(dialog.delete)()

        for user_id in users:
            await self.channel_layer.group_send(
                f'user_{user_id}',
                {
                    'type': 'dialog_deleted',
                    'dialog_id': dialog_id
                }
            )

    async def disconnect(self, close_code):
        if self.group_name:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def new_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'dialog_id': event['dialog_id'],
            'message': event['message'],
            'sender': event['sender'],
            'from_me': event.get('from_me', False),
        }))

    async def chat_typing(self, event):
        await self.send(text_data=json.dumps(event))

ONLINE_USERS_KEY = 'online_users'

class OnlineStatusConsumer(AsyncWebsocketConsumer):
    group_name = None
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

        count = cache.get(self.cache_key, 0) + 1
        cache.set(self.cache_key, count)

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

        await self.send(text_data=json.dumps({
            'type': 'online_users',
            'users': cache.get(ONLINE_USERS_KEY, [])
        }))

    async def disconnect(self, close_code):
        if self.group_name:
            count = cache.get(self.cache_key, 1) - 1

            if count <= 0:
                cache.delete(self.cache_key)

                await self.set_last_seen()

                online_users = set(cache.get(ONLINE_USERS_KEY, []))
                online_users.discard(self.user.id)
                cache.set(ONLINE_USERS_KEY, list(online_users))

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'user_offline',
                        'user_id': self.user.id,
                        'last_seen': timezone.now().isoformat(),
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
        await self.send(text_data=json.dumps({
            'type': 'user_offline',
            'user_id': event['user_id'],
            'last_seen': event.get('last_seen')
        }))

    @database_sync_to_async
    def set_last_seen(self):
        self.user.last_seen = timezone.now()
        self.user.save(update_fields=['last_seen'])
