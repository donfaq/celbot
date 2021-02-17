import argparse
import logging
import os

from bots import DiscordBot

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("bot", choices=["discord", "telegram"])
    return parser.parse_args()


if __name__ == '__main__':
    args = arguments()

    if args.bot == "discord":
        client = DiscordBot(broker_uri=os.getenv("REDIS_URL"))
        client.run(os.getenv("DISCORD_TOKEN"))
    elif args.bot == "telegram":
        pass
    else:
        pass
