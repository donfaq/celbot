import logging

import discord

from bots.utils import CeleryWrapper


class DiscordBot(discord.Client):
    def __init__(self, broker_uri, **options):
        super().__init__(**options)
        self.celery = CeleryWrapper(broker_uri)
        self.logger = logging.getLogger(self.__class__.__name__)

    def __save_msg(self, message: discord.Message):
        self.celery.save_msg(
            dt=message.created_at,
            source=f"{message.guild}#{message.channel}",
            author=f"{message.author.name}#{message.author.discriminator}",
            text=message.content
        )

    async def on_message(self, message: discord.Message):
        self.logger.info("MSG:[%s#%s@%s]:'%s'", message.guild, message.channel, message.author.name, message.content)
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!news'):
            await message.reply(self.celery.news())
        if message.content.startswith("!joke"):
            await message.reply(self.celery.joke())

        self.__save_msg(message)
