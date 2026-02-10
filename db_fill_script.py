import os
import random

import django
from django.db import transaction
from django.db.models import Count

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_blog.settings")
django.setup()

from users.models import CustomUser, UserFollow
from posts.models import Post, PostLike, Comment, CommentLike
from chat.models import Dialog, Message, MessageLike

from faker import Faker

fake = Faker("ru_RU")

with transaction.atomic():

    for i in range(30):
        CustomUser.objects.create_user(
            email=fake.email(),
            username=fake.user_name(),
            password=f'password{i}',
            bio=fake.text(max_nb_chars=33),
        )

    users = list(CustomUser.objects.all())

    for _ in range(100):
        follower, following = random.sample(users, 2)
        UserFollow.objects.get_or_create(
            follower=follower,
            following=following
        )

    posts = [
        Post(
            author=random.choice(users),
            content=fake.text(),
        )
        for _ in range(100)
    ]
    Post.objects.bulk_create(posts)

    posts = list(Post.objects.all())

    for _ in range(100):
        PostLike.objects.get_or_create(
            post=random.choice(posts),
            user=random.choice(users),
        )

    comments = [
        Comment(
            post=random.choice(posts),
            user=random.choice(users),
            text=fake.text(),
        )
        for _ in range(100)
    ]
    Comment.objects.bulk_create(comments)

    comments = list(Comment.objects.all())

    for _ in range(100):
        CommentLike.objects.get_or_create(
            comment=random.choice(comments),
            user=random.choice(users),
        )

    dialogs = []
    for _ in range(100):
        u1, u2 = random.sample(users, 2)
        if not Dialog.objects.filter(users=u1).filter(users=u2).exists():
            dialog = Dialog.objects.create()
            dialog.users.set([u1, u2])
            dialogs.append(dialog)

    messages = []
    for _ in range(1000):
        dialog = random.choice(dialogs)
        sender = random.choice(list(dialog.users.all()))
        messages.append(
            Message(
                dialog=dialog,
                sender=sender,
                text=fake.text(),
            )
        )
    Message.objects.bulk_create(messages)

    messages = list(Message.objects.all())
    for _ in range(1000):
        message = random.choice(messages)
        liker = random.choice(list(message.dialog.users.all()))
        MessageLike.objects.get_or_create(
            message=message,
            sender=liker,
        )
