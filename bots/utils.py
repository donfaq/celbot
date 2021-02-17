from celery import Celery


class CeleryWrapper:
    def __init__(self, broker_uri):
        self.celery = Celery('engine', broker=broker_uri, backend=broker_uri)

    def greet(self, name):
        return self.celery.send_task("greet", args=[name]).get()
