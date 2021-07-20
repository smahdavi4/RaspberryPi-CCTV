from telegram import Bot

tg_bot: Bot = None


def set_bot(bot_token):
    global tg_bot
    tg_bot = Bot(token=bot_token)


def send_message(chat_id, message):
    tg_bot.send_message(chat_id=chat_id, text=message)
