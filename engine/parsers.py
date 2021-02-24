import secrets

import cachetools.func
import ftfy
import requests
from bs4 import BeautifulSoup
from celery.utils.log import get_task_logger


def rand_choice(seq):
    return secrets.SystemRandom().choice(seq)


class AnekdotRuParser:
    def __init__(self):
        self.logger = get_task_logger(self.__class__.__name__)

    @cachetools.func.ttl_cache(maxsize=10, ttl=6000)
    def _get_random_anekdots(self):
        def parse_html(text):
            return list(map(lambda x: x.text, BeautifulSoup(text, features="html.parser").select("div[class=text]")))

        res = []
        url = "https://www.anekdot.ru/random/anekdot/"
        self.logger.info("Executing GET to %s", url)
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if r.ok:
            res = parse_html(r.text)
        return res

    def _get_text(self):
        res = None
        anekdots = self._get_random_anekdots()
        if anekdots:
            res = rand_choice(anekdots)
        return res

    def get_random_joke(self):
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


class BreakingMadParser:
    def __init__(self):
        self.logger = get_task_logger(self.__class__.__name__)

    def _download_popular_page(self, n=1) -> str:
        url = "http://breakingmad.me/ru/popular/"
        self.logger.info("Executing GET to %s?page=%d", url, n)
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

    def get_random_news(self):
        text = "Новостей не нашлось :("
        res = self._get_random_news()
        if res:
            text = res
        return text
