import os

from celery import Celery

from engine.tasks import GreetingTask, HaikuDetector

app = Celery(
    'engine',
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL"),
    include=['engine.tasks']
)
app.conf.update(
    result_expires=3600,
)
app.register_task(GreetingTask)
app.register_task(HaikuDetector)

if __name__ == '__main__':
    app.start()
