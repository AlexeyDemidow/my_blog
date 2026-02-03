from django.core.mail import send_mail


def send_email(user_name, user_email):
    send_mail(
        'Cпасибо что выбрали my_blog!',
        f'{user_name}, cпасибо что выбрали наc!\n'
        'Предлагаем вам создать свой первый пост! Пройдите по ссылке http://127.0.0.1:8000/\n'
        '\nС уважением, команда my_blog.',
        'usernzt@mail.ru',
        [user_email],
        fail_silently=False,
    )
