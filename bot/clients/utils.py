from datetime import datetime

from celery import Celery


class CeleryWrapper:
    def __init__(self, broker_uri):
        self.celery = Celery('engine', broker=broker_uri, backend=broker_uri)

    def greet(self, name):
        return self.celery.send_task("greet", args=[name]).get()

    def joke(self):
        return self.celery.send_task("anekdot").get()

    def news(self):
        return self.celery.send_task("breaking_mad").get()

    def speak(self, predicate: str = None):
        return self.celery.send_task("speak", [predicate]).get()

    def pron(self, predicate: str = None):
        return self.celery.send_task("pron", [predicate]).get()

    def kalik(self, predicate: str = None):
        return self.celery.send_task("kalik", [predicate]).get()

    def save_msg(self, dt: datetime, source: str, author: str, text: str):
        self.celery.send_task("save_msg", args=[dt, source, author, text])
