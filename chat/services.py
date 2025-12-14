from users.models import CustomUser
from .models import Dialog


def get_or_create_dialog(user1: CustomUser, user2: CustomUser) -> Dialog:
    dialog = (
        Dialog.objects
        .filter(users=user1)
        .filter(users=user2)
        .first()
    )

    if not dialog:
        dialog = Dialog.objects.create()
        dialog.users.add(user1, user2)

    return dialog
