import logging
import sys
import threading
import time
import argparse
from models import init_db, Schedules
from raspberry import cctv
from server_utils import server_uploader

from tgbot.tg_poller import start_bot
from tgbot.tg_sender import set_bot
from utils import create_schedule

file_handler = logging.FileHandler(filename='bog.log')
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO, handlers=handlers)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Parameters to be given to telegram bot.")
    parser.add_argument("--bot-token", type=str, required=True, help="Telegram Bot Token.")
    parser.add_argument("--server-addr", type=str, required=True, help="Server Address to send photos.")
    args = parser.parse_args()

    if len(list(Schedules.select())) == 0:
        create_schedule(Schedules.Sunday, "10:10", "20:20")
        create_schedule(Schedules.Monday, "10:10", "20:20")
        create_schedule(Schedules.All, "6:00", "11:00")

    init_db()
    set_bot(args.bot_token)
    server_uploader.initialize(bot_token=args.bot_token, server_address=args.server_addr)
    threading.Thread(target=start_bot, args=(args.bot_token,)).start()
    threading.Thread(target=cctv.start_watching).start()
    while True:
        time.sleep(10)
