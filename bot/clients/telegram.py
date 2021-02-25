import argparse
import html
import json
import logging
import os
import traceback

from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, Dispatcher

from bot.clients.utils import CeleryWrapper

logger = logging.getLogger(__name__)

BOT_TOKEN = str(os.getenv("TELEGRAM_TOKEN", "token"))
PUBLIC_PORT = int(os.getenv("PORT", '8080'))
PUBLIC_URL = os.getenv("PUBLIC_URL", "localhost")
DEVELOPER_CHAT_ID = int(os.getenv("DEV_CHAT_ID", 998969))

celery = CeleryWrapper(broker_uri=os.getenv("REDIS_URL"))


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", default="server", required=False, choices=["server", "local"])
    return parser.parse_args()


def bot_start_callback(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text(r"Привет\!", parse_mode=ParseMode.MARKDOWN_V2)


def error_callback(update: object, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )
    context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML)


def greet_callback(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text(celery.greet(update.message.from_user.name))


def joke_callback(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(celery.joke(), reply_to_message_id=update.message.message_id)


def news_callback(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(celery.news(), reply_to_message_id=update.message.message_id)


def get_predicate(update: Update):
    words = update.message.text.split()
    return words[1] if len(words) > 1 else None


def speak_callback(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(celery.speak(get_predicate(update)), reply_to_message_id=update.message.message_id)


def kalik_callback(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(celery.kalik(get_predicate(update)), reply_to_message_id=update.message.message_id)


def pron_callback(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(celery.pron(get_predicate(update)), reply_to_message_id=update.message.message_id)


def create_bot() -> Updater:
    """Start the bot."""
    updater = Updater(BOT_TOKEN, use_context=True)
    dp: Dispatcher = updater.dispatcher
    dp.add_handler(CommandHandler("start", bot_start_callback))
    dp.add_handler(CommandHandler("joke", joke_callback))
    dp.add_handler(CommandHandler("news", news_callback))
    dp.add_handler(CommandHandler("speak", speak_callback))
    dp.add_handler(CommandHandler("kalik", kalik_callback))
    dp.add_handler(CommandHandler("pron", pron_callback))
    dp.add_error_handler(error_callback)
    return updater


def run_webhook(updater: Updater) -> None:
    logger.info("Starting bot in webhook mode")

    webhook_url = "/".join((PUBLIC_URL.strip("/"), BOT_TOKEN))
    updater.start_webhook(listen="0.0.0.0", port=PUBLIC_PORT, url_path=BOT_TOKEN)
    updater.bot.set_webhook(webhook_url)
    updater.idle()


def run_polling(updater: Updater) -> None:
    logger.info("Starting bot in polling mode")
    updater.start_polling()
    updater.idle()


def start_telegram_bot():
    run_webhook(create_bot())


def main():
    args = arguments()

    if args.mode == "server":
        run_webhook(create_bot())
    else:
        run_polling(create_bot())


if __name__ == '__main__':
    main()
