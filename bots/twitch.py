import logging

import irc.bot
from irc.client import MessageTooLong

from bots.utils import CeleryWrapper


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

    def _author(self, msg_object):
        return msg_object.source.split("!")[0]

    def on_pubmsg(self, c, e):
        reaction_msg = self.celery.greet(self._author(e))
        try:
            self.connection.privmsg(self.channel, reaction_msg)
        except irc.client.MessageTooLong:
            self.log.exception(f"Message: '{reaction_msg}' seems to be too long for Twitch")
        except Exception:
            self.log.exception(f"Error sending message: '{reaction_msg}'")
