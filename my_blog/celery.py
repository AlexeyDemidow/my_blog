import os

from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_blog.settings')

app = Celery('my_blog')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-message': {
        'task': 'users.tasks.beat_mailing',
        # 'schedule': crontab(minute='*/3'), # тест
        'schedule': crontab(0, 0, day_of_month='3'),
    },
}