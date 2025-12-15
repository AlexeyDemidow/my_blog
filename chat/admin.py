from django.contrib import admin
from .models import Dialog, Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'dialog',
        'sender',
        'short_text',
        'created_at',
        'is_read',
    )
    list_filter = ('is_read', 'created_at')
    search_fields = ('text', 'sender__username')
    readonly_fields = ('created_at',)

    def short_text(self, obj):
        return obj.text[:40]

    short_text.short_description = 'Текст'


@admin.register(Dialog)
class DialogAdmin(admin.ModelAdmin):
    list_display = ('id', 'users_list', 'created_at')
    filter_horizontal = ('users',)
    readonly_fields = ('created_at',)

    def users_list(self, obj):
        return ', '.join(user.username for user in obj.users.all())

    users_list.short_description = 'Участники'

