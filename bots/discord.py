import discord
from bots.utils import CeleryWrapper


class DiscordBot(discord.Client):
    def __init__(self, broker_uri, **options):
        super().__init__(**options)
        self.celery = CeleryWrapper(broker_uri)

    async def on_message(self, message: discord.Message):
        if message.author.name != self.user.name:
            await message.channel.send(
                self.celery.greet(message.author.name)
            )
