import logging
from datetime import datetime

import irc.bot
import irc.strings

from bot.clients.utils import CeleryWrapper


class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, broker_uri, username, token, channel_name):
        self.log = logging.getLogger(self.__class__.__name__)
        self.celery = CeleryWrapper(broker_uri=broker_uri)

        self.channel = f"#{channel_name}".lower()
        self.log.info("Connecting to twitch IRC server: irc.chat.twitch.tv:6667")
        irc.bot.SingleServerIRCBot.__init__(
            self, [("irc.chat.twitch.tv", 6667, "oauth:{}".format(token))], username, username
        )
        self.log.info("Connected to twitch IRC")

    def on_welcome(self, c, e):
        self.log.info("Joining {}".format(self.channel))
        c.cap("REQ", ":twitch.tv/membership")
        c.cap("REQ", ":twitch.tv/tags")
        c.cap("REQ", ":twitch.tv/commands")
        c.join(self.channel)
        self.log.info("Successfully joined to {}".format(self.channel))

    def __author(self, event):
        return event.source.split("!")[0]

    def __msg(self, event):
        return event.arguments[0]

    def __predicate(self, msg):
        words = msg.split()
        return words[1] if len(words) > 1 else None

    def __get_ts(self, event):
        for tag in event.tags:
            if tag["key"] == 'tmi-sent-ts':
                return datetime.utcfromtimestamp(float(tag["value"]) / 1000)

    def __save_msg(self, event):
        self.celery.save_msg(
            dt=self.__get_ts(event),
            source=f"twitch{self.channel}",
            author=self.__author(event),
            text=self.__msg(event)
        )

    def __send_message(self, text):
        self.connection.privmsg(self.channel, text)

    def on_pubmsg(self, connection, event):
        try:
            author = self.__author(event)
            msg = self.__msg(event)
            if len(msg) > 0:
                if msg.startswith("!"):
                    self.log.info(f"Reacting to command from user @{author}: '{msg}'")
                    if msg.startswith("!news"):
                        self.__send_message(self.celery.news())
                    elif msg.startswith("!joke"):
                        self.__send_message(self.celery.joke())
                    elif msg.startswith("!kalik"):
                        self.__send_message(self.celery.kalik(predicate=self.__predicate(msg)))
                    elif msg.startswith("!pron"):
                        self.__send_message(self.celery.pron(predicate=self.__predicate(msg)))
                    elif msg.startswith("!speak"):
                        self.__send_message(self.celery.speak(predicate=self.__predicate(msg)))
                    elif msg.startswith("!gachi"):
                        self.__send_message(self.celery.gachi_horo(max_size=250))
                    else:
                        self.__send_message(f"@{author} нет такой команды")
                else:
                    self.log.info(f"Saving msg @{author}:'{msg}'")
                    self.__save_msg(event)
        except Exception as e:
            self.log.exception("Unexpected error", e)
