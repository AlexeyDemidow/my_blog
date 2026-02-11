from django.contrib import admin
from .models import Dialog, Message, DialogUser


class DialogUserInline(admin.TabularInline):
    model = DialogUser
    extra = 0


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
    readonly_fields = ('created_at',)
    inlines = (DialogUserInline,)

    def users_list(self, obj):
        return ', '.join(
            du.user.username for du in obj.dialog_users.select_related('user')
        )

    users_list.short_description = 'Участники'


