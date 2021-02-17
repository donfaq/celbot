import argparse
import os

from bots import DiscordBot


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("bot", choices=["discord", "telegram"])
    return parser.parse_args()


if __name__ == '__main__':
    args = arguments()

    if args.bot == "discord":
        client = DiscordBot(broker_uri=os.getenv("CELERY_BROKER_URI"))
        client.run(os.getenv("DISCORD_TOKEN"))
    elif args.bot == "telegram":
        pass
    else:
        pass
