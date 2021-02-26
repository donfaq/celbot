import logging
import os

from celery import Celery

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

app = Celery(
    'engine',
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL"),
    include=['bot.engine.tasks']
)
app.config_from_object('bot.engine.celery_settings')

if __name__ == '__main__':
    app.start()
