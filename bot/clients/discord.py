import logging

import discord

from bot.clients.utils import CeleryWrapper


class DiscordBot(discord.Client):
    def __init__(self, broker_uri, **options):
        super().__init__(**options)
        self.celery = CeleryWrapper(broker_uri)
        self.logger = logging.getLogger(self.__class__.__name__)

    def __save_msg(self, message: discord.Message):
        self.celery.save_msg(
            dt=message.created_at,
            source=f"discord#{message.guild}#{message.channel}",
            author=f"{message.author.name}#{message.author.discriminator}",
            text=message.content
        )

    def __get_predicate(self, message: discord.Message):
        words = message.content.split()
        return words[1] if len(words) > 1 else None

    async def on_message(self, message: discord.Message):
        self.logger.info("MSG:[%s#%s@%s]:'%s'", message.guild, message.channel, message.author.name, message.content)
        if message.author.id == self.user.id:
            return
        elif message.content.startswith('!news'):
            await message.reply(self.celery.news())
        elif message.content.startswith("!joke"):
            await message.reply(self.celery.joke())
        elif message.content.startswith("!speak"):
            await message.reply(self.celery.speak(self.__get_predicate(message)))
        elif message.content.startswith("!kalik"):
            await message.reply(self.celery.kalik(self.__get_predicate(message)))
        elif message.content.startswith("!pron"):
            await message.reply(self.celery.pron(self.__get_predicate(message)))
        elif message.content.startswith("!gachi"):
            await message.reply(self.celery.gachi_horo(self.__get_predicate(message)))
        else:
            self.__save_msg(message)
