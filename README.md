## Блог типа Treads

---
### Для запуска Celery нужно совершить следующие шаги:
- Redis запускался в docker-контейнере по команде:
`docker run -d -p 6379:6379 redis`
- Для ОС Windows REDIS_HOST должен быть равен 'localhost' или '127.0.0.1'
И запускать worker командой:
`celery -A project-name worker --pool=solo -l info`
- Запускать beat командой:
`celery -A project-name beat -l info`
- Для запуска flower:
`celery -A project-name flower`
- Или отслеживать выполненные задачи в admin панели