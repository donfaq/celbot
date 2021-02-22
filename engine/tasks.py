import os
import pathlib
import secrets

import cachetools.func
import ftfy
import requests
from bs4 import BeautifulSoup
from celery import Task
from celery.utils.log import get_task_logger
from rusyll import rusyll

from engine.database import DatabaseWrapper
from engine.files import StorageManager

logger = get_task_logger(__name__)


def rand_choice(seq):
    return secrets.SystemRandom().choice(seq)


class GreetingTask(Task):
    name = "greet"

    def run(self, name):
        logger.info("Replying with greet to %s message", name)
        return f"Hello, {name}"


class HaikuDetector(Task):
    name = "haiku"

    def run(self, text):
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


class AnekdotTask(Task):
    name = "anekdot"

    @cachetools.func.ttl_cache(maxsize=10, ttl=6000)
    def _get_random_anekdots(self):
        def parse_html(text):
            return list(map(lambda x: x.text, BeautifulSoup(text, features="html.parser").select("div[class=text]")))

        res = []
        r = requests.get("https://www.anekdot.ru/random/anekdot/", headers={"User-Agent": "Mozilla/5.0"})
        if r.ok:
            res = parse_html(r.text)
        return res

    def _get_text(self):
        res = None
        anekdots = self._get_random_anekdots()
        if anekdots:
            res = rand_choice(anekdots)
        return res

    def run(self):
        text = None
        tries = 0
        while tries < 5:
            text = self._get_text()
            if text is not None and len(text.encode('utf-8')) < 400:
                break
            tries += 1
        if text is None:
            text = "no u"
        return text


class BreakingMadTask(Task):
    name = "breaking_mad"

    def _download_popular_page(self, n=1) -> str:
        url = "http://breakingmad.me/ru/popular/"
        logger.info("Executing GET to %s", url)
        res = ""
        r = requests.get(url, params=dict(page=n))
        if r.ok:
            res = r.text
        return res

    @cachetools.func.ttl_cache(maxsize=10, ttl=6000)
    def _extract_news(self, raw_html):
        soup = BeautifulSoup(raw_html, features="html.parser")

        texts = list(
            map(lambda t: ftfy.fix_encoding(t), map(lambda x: x.text, soup.select("div[class=news-row] > h2"))))
        links = list(map(lambda l: l['href'], soup.select("div[class=news-row] span[href]")))

        return [' '.join([t, l]) for t, l in zip(texts, links)]

    def _get_random_news(self):
        res = None
        candidate_news = []
        for n in range(5):
            candidate_news += self._extract_news(self._download_popular_page(n))

        if candidate_news:
            candidate_news = list(set(candidate_news))
            res = rand_choice(candidate_news)

        return res

    def run(self):
        text = "Новостей не нашлось :("
        res = self._get_random_news()
        if res:
            text = res
        return text


class SaveMessageTask(Task):
    name = "save_msg"
    ignore_result = True

    def __init__(self):
        self.db = DatabaseWrapper(os.getenv("DATABASE_URL"))

    def run(self, dt, source: str, author: str, text: str, *args, **kwargs):
        self.db.save_new_message(dt=dt, source=source, author=author, text=text)


class GetModelsFolder(Task):
    name = "get_models"

    def __init__(self):
        self.storage = StorageManager(os.getenv("DROPBOX_TOKEN"))

    def run(self, *args, **kwargs) -> str:
        return str(self.storage.get_local_folder())
