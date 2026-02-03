
from django.core.mail import send_mail
from my_blog.celery import app
from .service import send_email
from .models import CustomUser


@app.task
def send_mailing(user_name, user_email):
    send_email(user_name, user_email)


@app.task
def beat_mailing():
    for user in CustomUser.objects.all():
        if user.username:
            send_mail(
                'my_blog',
                f'{user.username}, Пару советов для охватов:\n'
                'Заголовок (Тема) — это 80% успеха. Используй эмодзи (но в меру) и интригу.\n'
                'Добавь призыв к действию (CTA). Не просто «вот ссылка», а «поделись мнением в комментариях» или «сохрани, чтобы не потерять».\n'
                'Персонализация. Если сервис позволяет, всегда обращайся по имени.\n'
                'http://127.0.0.1:8000/\n',
                'usernzt@mail.ru',
                [user.email],
                fail_silently=False,
            )
        else:
            send_mail(
                'my_blog',
                f'{user}, Пару советов для охватов:\n'
                'Заголовок (Тема) — это 80% успеха. Используй эмодзи (но в меру) и интригу.\n'
                'Добавь призыв к действию (CTA). Не просто «вот ссылка», а «поделись мнением в комментариях» или «сохрани, чтобы не потерять».\n'
                'Персонализация. Если сервис позволяет, всегда обращайся по имени.\n'
                'http://127.0.0.1:8000/\n',
                'usernzt@mail.ru',
                [user.email],
                fail_silently=False,
            )
