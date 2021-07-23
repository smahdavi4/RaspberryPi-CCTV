import logging
import time
from datetime import datetime

from models import Schedules
from server_utils import server_uploader
from tgbot.tg_sender import send_image
from utils import get_schedules, get_subscribers


class CCTV:
    def __init__(self):
        pass

    def take_photo(self):
        # TODO: Take a photo
        with open('temp.png', 'rb') as f:
            data = f.read()
        return data

    def is_active_schedule(self):
        schedules = get_schedules()
        date_now = datetime.now()
        for schedule in schedules:
            week_ok = schedule.weekday == Schedules.WEEKDAYS[date_now.weekday()] or schedule.weekday == Schedules.All
            time_ok = schedule.start_time <= date_now.time() <= schedule.end_time
            if week_ok and time_ok:
                return True
        return False

    def braodcast_photo(self, photo_data):
        server_uploader.send_image(image_data=photo_data, image_date=datetime.now())
        return # TODO: Fix it
        for chat_id in get_subscribers():
            try:
                send_image(chat_id=chat_id, image_data=photo_data, caption="Hi")
            except Exception as e:
                logging.exception(e)

    def start_watching(self):
        while True:
            if self.is_active_schedule():
                photo_data = self.take_photo()
                self.braodcast_photo(photo_data=photo_data)
            time.sleep(2)


cctv = CCTV()
