import logging

import discord

from bots.utils import CeleryWrapper


class DiscordBot(discord.Client):
    def __init__(self, broker_uri, **options):
        super().__init__(**options)
        self.celery = CeleryWrapper(broker_uri)
        self.logger = logging.getLogger(self.__class__.__name__)

    async def on_message(self, message: discord.Message):
        self.logger.info("MSG [%s#%s] %s - %s", message.guild, message.channel, message.author.name, message.content)
        if message.author.name != self.user.name:
            await message.channel.send(
                self.celery.greet(message.author.name)
            )
