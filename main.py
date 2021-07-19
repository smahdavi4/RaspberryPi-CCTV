import logging
import threading
import time
import argparse
import models
from tgbot import start_bot

logging.basicConfig(filename='bog.log', format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Parameters to be given to telegram bot.")
    parser.add_argument("--bot-token", type=str, required=True, help="Telegram Bot Token.")
    args = parser.parse_args()

    threading.Thread(target=start_bot, args=(args.bot_token,)).start()
    while True:
        time.sleep(10)
