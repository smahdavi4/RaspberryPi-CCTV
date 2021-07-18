import logging

from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler


def _start_command(update: Update, context: CallbackContext):
    update.message.reply_text("Hi, Wecome!")
    logging.info(f"Welcome {update.effective_chat.id}")


def start_bot(bot_token: str):
    updater = Updater(bot_token)
    updater.dispatcher.add_handler(CommandHandler("start", _start_command))
    updater.start_polling()
