import os

from celery import Celery

app = Celery(
    'engine',
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL"),
    include=['bot.engine.tasks']
)
app.config_from_object('bot.engine.celery_settings')

if __name__ == '__main__':
    app.start()
