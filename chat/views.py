from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from users.models import CustomUser
from .models import Dialog
from .services import get_or_create_dialog


@login_required
def start_dialog(request, user_id):
    other_user = CustomUser.objects.get(id=user_id)
    dialog = get_or_create_dialog(request.user, other_user)
    return redirect('chat:dialog', dialog_id=dialog.id)


@login_required
def dialog_view(request, dialog_id):
    dialog = get_object_or_404(Dialog, id=dialog_id)

    if request.user not in dialog.users.all():
        return JsonResponse({'status': 'error', 'message': 'not found or forbidden'}, status=403)

    messages = dialog.messages.select_related('sender').order_by('created_at')

    return render(request, 'chat.html', {
        'dialog': dialog,
        'messages': messages,
    })
