from django.db import models
from users.models import CustomUser


class Dialog(models.Model):
    users = models.ManyToManyField(CustomUser, related_name='dialogs')
    created_at = models.DateTimeField(auto_now_add=True)

    is_pinned = models.BooleanField(default=False)
    pinned_at = models.DateTimeField(null=True, blank=True)

    @property
    def companion(self):
        return self.users.exclude(id=self._current_user.id).first()

    def __str__(self):
        return f'Dialog {self.id}'


class Message(models.Model):
    dialog = models.ForeignKey(Dialog, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    is_pinned = models.BooleanField(default=False)
    pinned_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.sender}: {self.text[:20]}'


class MessageLike(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='message_likes')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'sender')