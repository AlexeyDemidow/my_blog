from django.db.models import Max
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView

from users.models import CustomUser
from .models import Dialog
from .services import get_or_create_dialog


class DialogList(ListView):
    model = Dialog
    context_object_name = 'chats'
    template_name = 'chat_list.html'

    def get_queryset(self):
        qs = (
            Dialog.objects
            .filter(users=self.request.user)
            .prefetch_related('users', 'messages')
        )

        # 🔥 прокидываем текущего пользователя в каждый объект
        for dialog in qs:
            dialog._current_user = self.request.user

        return qs


@login_required
def start_dialog(request, user_id):
    other_user = CustomUser.objects.get(id=user_id)
    dialog = get_or_create_dialog(request.user, other_user)
    return redirect('dialog', dialog_id=dialog.id)


@login_required
def dialog_view(request, dialog_id):
    dialog = Dialog.objects.get(id=dialog_id)

    # помечаем сообщения как прочитанные
    dialog.messages.filter(
        is_read=False
    ).exclude(sender=request.user).update(is_read=True)

    messages = dialog.messages.select_related('sender')

    return render(request, 'chat.html', {
        'dialog': dialog,
        'messages': messages
    })
