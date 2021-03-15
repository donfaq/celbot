import secrets
from datetime import datetime

import cachetools.func
import ftfy
import requests
from bs4 import BeautifulSoup
from celery.utils.log import get_task_logger


def rand_choice(seq):
    return secrets.SystemRandom().choice(seq)


def get_short_link(url: str):
    return requests.get(f"https://clck.ru/--?url={url}").text


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


class YNewsParser:
    __news: list = None
    __news_updated_at: datetime = None

    def __init__(self):
        self.logger = get_task_logger(self.__class__.__name__)
        self.logger.info(f"Initializing {self.__class__.__name__}")

    def __download_news_page(self):
        self.logger.info("Downloading yandex.ru/news page")
        return requests.get("https://yandex.ru/news").text

    @staticmethod
    def __parse_ya_news(text):
        result = []
        soup = BeautifulSoup(text, features="html.parser")
        for i, card in enumerate(soup.select(".mg-card__text-content")[:5], start=1):
            result.append({
                "n": i,
                "title": " ".join(card.select_one(".mg-card__title").text.split()),
                "link": get_short_link(card.select_one(".mg-card__link")['href'].split("?")[0]),
                "annotation": " ".join(card.select_one(".mg-card__annotation").text.split())
            })
        return result

    @property
    def top_news(self) -> list:
        self.logger.info("news=%s; updated_at=%s", self.__news, self.__news_updated_at)
        if self.__news and self.__news_updated_at:
            if (datetime.now() - self.__news_updated_at).total_seconds() < 300:
                return self.__news
        self.__news = self.__parse_ya_news(self.__download_news_page())
        self.__news_updated_at = datetime.now()
        return self.__news
