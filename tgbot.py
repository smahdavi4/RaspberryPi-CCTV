import logging

from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters

from utils import create_user, activate_user, is_user_active, delete_user


def active_user_required(command_func):
    def wrapper(update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        if is_user_active(chat_id):
            command_func(update, context)
        else:
            update.message.reply_text("Please activate your account first.")

    return wrapper


def _print_new_password(full_name, chat_id, passwd):
    log = f"Password for user <{full_name}, {chat_id}>: {passwd}"
    logging.info(log)
    print(log)


def _extract_user_information(update: Update):
    chat_id = update.effective_chat.id
    full_name = f"{update.effective_user.first_name} {update.effective_user.last_name}"
    return chat_id, full_name


def _start_command(update: Update, context: CallbackContext):
    chat_id, full_name = _extract_user_information(update)
    passwd = create_user(chat_id)
    if passwd is None:
        update.message.reply_text("You are already registered.")
    else:
        _print_new_password(full_name, chat_id, passwd)
        update.message.reply_text("Please enter the password shown on your bot log file.")


def _enter_password_command(update: Update, context: CallbackContext):
    chat_id, full_name = _extract_user_information(update)
    passwd = update.message.text
    success, new_passwd = activate_user(chat_id, passwd)

    if success:
        update.message.reply_text("Account Activated Successfully.")
    else:
        update.message.reply_text("Wrong Password. Try again with the new password shown on your bot log file.")
    if new_passwd is not None:
        _print_new_password(full_name, chat_id, new_passwd)


@active_user_required
def _unsubscribe_command(update: Update, context: CallbackContext):
    chat_id, _ = _extract_user_information(update)
    delete_user(chat_id)
    update.message.reply_text("Unsubscribed successfully.")


def start_bot(bot_token: str):
    updater = Updater(bot_token)
    updater.dispatcher.add_handler(CommandHandler("start", _start_command))
    updater.dispatcher.add_handler(CommandHandler("unsubscribe", _unsubscribe_command))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('\\d{5}'), _enter_password_command))
    updater.start_polling()
