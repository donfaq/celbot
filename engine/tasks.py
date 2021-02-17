from celery import Task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class GreetingTask(Task):
    name = "greet"

    def run(self, name):
        logger.info("Replying with greet to %s message", name)
        return f"Hello, {name}"
