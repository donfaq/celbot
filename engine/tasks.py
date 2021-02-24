import os
import pathlib

from celery import current_app
from celery.utils.log import get_task_logger
from rusyll import rusyll

from engine.chain import MarkovifyWrapper
from engine.database import DatabaseWrapper
from engine.files import StorageManager
from engine.parsers import AnekdotRuParser, BreakingMadParser

logger = get_task_logger(__name__)
storage = StorageManager(os.getenv("DROPBOX_TOKEN"))
database_wrapper = DatabaseWrapper(os.getenv("DATABASE_URL"))
local_folder = pathlib.Path(storage.get_local_folder())
chat_model_chain = MarkovifyWrapper(local_folder.joinpath("chat_model"), database_wrapper)
kalik_model_chain = MarkovifyWrapper(local_folder.joinpath("kalik_model"))
pron_model_chain = MarkovifyWrapper(local_folder.joinpath("pron_model"))
anekdot_parser = AnekdotRuParser()
breaking_mad_parser = BreakingMadParser()


@current_app.task(name="greet")
def greet(name: str):
    logger.info("Replying with greet to %s message", name)
    return f"Hello, {name}"


@current_app.task(name="haiku")
def haiku(text: str):
    max_syllables = (5, 7, 5)
    n_syllables = rusyll.token_to_syllables(text)

    if len(n_syllables) == 17:
        haiku = [[], [], []]
        words = text.split()

        row_num = 0
        for word in words:
            haiku[row_num].append(word)
            syllables_count = len(rusyll.token_to_syllables(' '.join(haiku[row_num])))
            if syllables_count == max_syllables[row_num]:
                row_num += 1
                continue
            if syllables_count > max_syllables[row_num]:
                return None
        return '\n'.join(map(lambda line: ' '.join(line), haiku))
    return None


@current_app.task(name="breaking_mad")
def breaking_mad():
    return breaking_mad_parser.get_random_news()


@current_app.task(name="anekdot")
def anekdot():
    return anekdot_parser.get_random_joke()


@current_app.task(name="save_msg")
def save_msg(dt, source: str, author: str, text: str):
    return database_wrapper.save_new_message(dt=dt, source=source, author=author, text=text)


@current_app.task(name="speak")
def speak(predicate: str = None):
    return chat_model_chain.generate(predicate=predicate)


@current_app.task(name="pron")
def speak(predicate: str = None):
    return pron_model_chain.generate(predicate=predicate)


@current_app.task(name="kalik")
def speak(predicate: str = None):
    return kalik_model_chain.generate(predicate=predicate)
