from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Max, Count, Q, OuterRef, Subquery, Exists
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from posts.models import Post
from users.models import CustomUser
from .models import Dialog, Message, MessageLike
from .services import get_or_create_dialog



class DialogList(LoginRequiredMixin, ListView):
    model = Dialog
    context_object_name = 'chats'
    template_name = 'chat_list.html'

    def get_queryset(self):
        user = self.request.user

        last_message_subquery = Message.objects.filter(
            dialog=OuterRef('pk')
        ).order_by('-created_at')

        qs = (
            Dialog.objects
            .filter(users=user)
            .annotate(
                last_message_text=Subquery(last_message_subquery.values('text')[:1]),
                last_message_time=Subquery(last_message_subquery.values('created_at')[:1]),
                unread_count=Count(
                    'messages',
                    filter=Q(
                        messages__is_read=False
                    ) & ~Q(
                        messages__sender=user
                    )
                )
            )
            .prefetch_related('users')
            .order_by(
                '-is_pinned',
                '-pinned_at',
                '-last_message_time'
            )
        )
        for dialog in qs:
            dialog._current_user = user

        return qs


@login_required
def start_dialog(request, user_id):
    other_user = CustomUser.objects.get(id=user_id)
    dialog = get_or_create_dialog(request.user, other_user)
    return redirect('dialog', dialog_id=dialog.id)


@login_required
def dialog_view(request, dialog_id):
    dialog = get_object_or_404(Dialog, id=dialog_id, users=request.user)
    dialog.messages.filter(
        is_read=False
    ).exclude(sender=request.user).update(is_read=True)

    base_qs = (
        Message.objects
        .filter(dialog=dialog)
        .select_related(
            'sender',
            'sent_post',
            'sent_post__author',
            'sent_post__original_post',
            'sent_post__original_post__author',
        )
        .prefetch_related(
            'sent_post__images',
            'sent_post__original_post__images',
        )
        .annotate(
            is_liked=Exists(
                MessageLike.objects.filter(
                    message=OuterRef('pk'),
                    sender=request.user,
                )
            )
        )
        .order_by('-is_pinned', '-pinned_at', '-created_at')
    )

    dialog._current_user = request.user

    pinned_messages = reversed(base_qs.filter(is_pinned=True)[:20])
    messages = reversed(base_qs.filter(is_pinned=False)[:20])

    return render(request, 'chat.html', {
        'dialog': dialog,
        'messages': messages,
        'pinned_messages': pinned_messages,
    })


@login_required
@require_POST
def send_post(request, post_id, dialog_id):
    dialog = Dialog.objects.get(id=dialog_id)
    post = get_object_or_404(Post, id=post_id)

    if request.user not in dialog.users.all():
        return JsonResponse({'status': 'error'}, status=403)

    new_message = Message.objects.create(
        sender=request.user,
        dialog=dialog,
        sent_post=post,
        text=request.POST.get("text", "").strip()
    )

    return JsonResponse({
        'status': 'success',
        'id': new_message.id,
        'author': new_message.sender.username,
        'text': new_message.text,
        'created_at': new_message.created_at.strftime('%H:%M'),

        # данные поста
        'post': {
            'id': post.id,
            'avatar': str(post.author.avatar),
            'author': post.author.username,
            'content': post.content,
            'images': [img.image.url for img in post.images.all()]
        }
    })

@login_required
@require_POST
def toggle_pin(request, dialog_id):
    chat = Dialog.objects.get(
        id=dialog_id,
        users=request.user
    )

    chat.is_pinned = not chat.is_pinned
    chat.pinned_at = timezone.now() if chat.is_pinned else None
    chat.save()

    return JsonResponse({
        'is_pinned': chat.is_pinned
    })

@login_required
@require_POST
def toggle_message_pin(request, dialog_id, message_id):
    message = get_object_or_404(
        Message,
        id=message_id,
        dialog_id=dialog_id
    )
    message.is_pinned = not message.is_pinned
    message.pinned_at = timezone.now() if message.is_pinned else None
    message.save()

    return JsonResponse({
        'is_pinned': message.is_pinned
    })


@login_required
def like_unlike_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    message_like, created = MessageLike.objects.get_or_create(sender=request.user, message=message)
    if not created:
        message_like.delete()
        is_liked = False
    else:
        is_liked = True

    return JsonResponse({
        'status': 'success',
        'is_liked': is_liked,
        'like_count': message.message_likes.count()
    })

@login_required
def pag_messages(request, dialog_id):
    dialog = get_object_or_404(Dialog, id=dialog_id, users=request.user)

    page = int(request.GET.get('page', 1))
    page_size = 20

    messages_qs = (
        Message.objects
        .filter(dialog=dialog, is_pinned=False)
        .select_related('sender')
        .order_by('-created_at')
    )

    paginator = Paginator(messages_qs, page_size)
    messages = paginator.get_page(page)

    html = render_to_string(
        'partials/messages_page.html',
        {
            'messages': reversed(messages),
            'request': request
        }
    )

    return JsonResponse({
        'html': html,
        'has_next': messages.has_next()
    })