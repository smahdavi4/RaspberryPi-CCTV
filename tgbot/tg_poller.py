import logging

from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, ConversationHandler

from utils import create_user, activate_user, is_user_active, delete_user, create_schedule, delete_schedule, \
    get_schedules

WELCOME_TEXT = """
Welcome to the cctv bot. Here is the list of commands you can work with:
✅/subscribe - Register and subscribe to cctv.
✅/unsubscribe - Delete your registration and unsubscribe from updates. 
✅/add_schedule - Add a schedule
✅/remove_schedule - Remove a schedule
✅/show_schedules - Show all active schedules
"""


class SubscribeSates:
    ENTER_PASSWORD = 0


class ScheduleStates:
    REMOVE_SCHEDULE = 0
    ADD_SCHEDULE = 0


def active_user_required(command_func):
    def wrapper(update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        if is_user_active(chat_id):
            return command_func(update, context)
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
    update.message.reply_text(WELCOME_TEXT)


def _subscribe_command(update: Update, context: CallbackContext):
    chat_id, full_name = _extract_user_information(update)
    passwd = create_user(chat_id)
    if passwd is None:
        update.message.reply_text("You are already registered.")
        return ConversationHandler.END
    else:
        _print_new_password(full_name, chat_id, passwd)
        update.message.reply_text("Please enter the password shown on your bot log file.")
        return SubscribeSates.ENTER_PASSWORD


def _enter_password_command(update: Update, context: CallbackContext):
    chat_id, full_name = _extract_user_information(update)
    passwd = update.message.text
    success, new_passwd = activate_user(chat_id, passwd)

    if new_passwd is not None:
        _print_new_password(full_name, chat_id, new_passwd)
    if success:
        update.message.reply_text("Account Activated Successfully.")
        return ConversationHandler.END
    else:
        update.message.reply_text("Wrong Password. Try again with the new password shown on your bot log file.")
        return SubscribeSates.ENTER_PASSWORD


def _invalid_command(update: Update, context: CallbackContext):
    update.message.reply_text("Invalid Input.")
    return ConversationHandler.END


@active_user_required
def _unsubscribe_command(update: Update, context: CallbackContext):
    chat_id, _ = _extract_user_information(update)
    delete_user(chat_id)
    update.message.reply_text("Unsubscribed successfully.")


@active_user_required
def _add_schedule_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Please enter your schedule with the following format:\nstart_time end_time weekday\n"
        "Example1: 10:10 18:30 Sunday\n"
        "Example2: 6:30 8:10 All"
    )
    return ScheduleStates.ADD_SCHEDULE


def _add_one_schedule(update: Update, context: CallbackContext):
    # update.message.reply_text("Hi")
    text = update.message.text
    start_time, end_time, weekday = text.split()
    try:
        create_schedule(start_time, end_time, weekday)
        update.message.reply_text("Schedule was created successfully.")
        return ConversationHandler.END
    except Exception as e:
        logging.exception(e)
        update.message.reply_text("Invalid Format. Please re-enter your schedule time.")
        return ScheduleStates.ADD_SCHEDULE


@active_user_required
def _remove_schedule_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Please enter the id of the schedule you wish to remove. You can find the ids of each schedule "
        "by using show_schedules command"
    )
    return ScheduleStates.REMOVE_SCHEDULE


def _remove_one_schedule(update: Update, context: CallbackContext):
    schedule_id = int(update.message.text)
    try:
        delete_schedule(schedule_id)
        update.message.reply_text("Removed schedule successfully.")
        return ConversationHandler.END
    except Exception as e:
        logging.exception(e)
        update.message.reply_text("Invalid Schedule, re-enter your schedule id.")
        return ScheduleStates.REMOVE_SCHEDULE


@active_user_required
def _show_schedules_command(update: Update, context: CallbackContext):
    schedules = get_schedules()
    response = "List of schedules:\nid - start - end - weekday\n{}".format(
        '\n'.join([repr(schedule) for schedule in schedules])
    )
    update.message.reply_text(response)


def start_bot(bot_token: str):
    updater = Updater(bot_token)

    subscribe_handler = ConversationHandler(
        entry_points=[CommandHandler("subscribe", _subscribe_command)],
        states={
            SubscribeSates.ENTER_PASSWORD: [
                MessageHandler(Filters.regex('^\\d{5}$'), _enter_password_command)
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('.*'), _invalid_command)]
    )

    add_schedule_handler = ConversationHandler(
        entry_points=[CommandHandler("add_schedule", _add_schedule_command)],
        states={
            ScheduleStates.ADD_SCHEDULE: [
                MessageHandler(Filters.regex('^[0-9:]+ [0-9:]+ \\w+$'), _add_one_schedule)
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('.*'), _invalid_command)]
    )

    remove_schedule_handler = ConversationHandler(
        entry_points=[CommandHandler("remove_schedule", _remove_schedule_command)],
        states={
            ScheduleStates.REMOVE_SCHEDULE: [
                MessageHandler(Filters.regex('^\\d+$'), _remove_one_schedule)
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('.*'), _invalid_command)]
    )

    updater.dispatcher.add_handler(CommandHandler("start", _start_command))
    updater.dispatcher.add_handler(subscribe_handler)
    updater.dispatcher.add_handler(CommandHandler("unsubscribe", _unsubscribe_command))

    updater.dispatcher.add_handler(add_schedule_handler)
    updater.dispatcher.add_handler(remove_schedule_handler)
    updater.dispatcher.add_handler(CommandHandler("show_schedules", _show_schedules_command))
    updater.start_polling()
