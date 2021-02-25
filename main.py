import argparse
import logging
import os

from bot.clients import DiscordBot, start_telegram_bot, TwitchBot

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("bot", choices=["discord", "telegram", "twitch"])
    return parser.parse_args()


if __name__ == '__main__':
    args = arguments()

    if args.bot == "discord":
        DiscordBot(
            broker_uri=os.getenv("REDIS_URL")
        ).run(os.getenv("DISCORD_TOKEN"))
    elif args.bot == "telegram":
        start_telegram_bot()
    elif args.bot == "twitch":
        TwitchBot(
            broker_uri=os.getenv("REDIS_URL"),
            username=os.getenv("TWITCH_USERNAME"),
            token=os.getenv("TWITCH_TOKEN"),
            channel_name=os.getenv("TWITCH_CHANNEL")
        ).start()
    else:
        raise ValueError("Illegal argument")
