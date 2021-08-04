import io
import logging
import time
from datetime import datetime

try:
    from picamera import PiCamera
except ImportError:
    logging.error("Can't import picamera. Please make sure picamera is installed and you run the code on raspberrypi.")
import numpy as np
from PIL import Image
from models import Schedules
from server_utils import server_uploader
from tgbot.tg_sender import send_image
from utils import get_schedules, get_subscribers


class ImageManager:
    MAX_IMAGE_BUFFER = 20
    IMAGE_QUANTIZATION_BINS = np.arange(0, 256, 30)
    NEW_IMAGE_THRESHOLD = 0.1
    SUSPICIOUS_IMAGE_THRESHOLD = 0.25

    def __init__(self):
        self.images = []

    def clear(self):
        self.images.clear()

    def quantize(self, arr_rgb):
        bins = ImageManager.IMAGE_QUANTIZATION_BINS
        arr = arr_rgb.mean(axis=2)
        inds = np.digitize(arr, bins)
        return bins[inds]

    def diff_images(self, im1, im2):
        diff_num = (im1 != im2).sum() / np.prod(im1.shape)
        diff_pix = np.abs(im1 - im2).sum()
        return diff_pix, diff_num

    def next_image(self, new_image: np.ndarray):
        self.images.append(self.quantize(new_image))
        # np.save("{}.npy".format(datetime.now().strftime('%d-%m-%Y-%H-%M-%S')), new_image)
        if len(self.images) > ImageManager.MAX_IMAGE_BUFFER:
            self.images.pop(0)

    def is_image_new(self, new_image: np.ndarray):
        quantized_img = self.quantize(new_image)
        if len(self.images) == 0:
            return True
        last_image = self.images[-1]
        _, diff_num_pixels = self.diff_images(quantized_img, last_image)
        return diff_num_pixels > ImageManager.NEW_IMAGE_THRESHOLD

    def is_image_suspicious(self, new_image: np.ndarray):
        quantized_img = self.quantize(new_image)
        if len(self.images) == 0:
            return False
        last_image = self.images[-1]
        _, diff_num_pixels = self.diff_images(quantized_img, last_image)
        return diff_num_pixels > ImageManager.SUSPICIOUS_IMAGE_THRESHOLD


class CCTV:
    def __init__(self):
        self.camera = None
        self._is_camera_open = False
        self._image_manager = ImageManager()
        self._open_camera()

    def _open_camera(self):
        if self._is_camera_open:
            return
        self.camera = PiCamera()
        self._is_camera_open = True

    def _close_camera(self):
        if self._is_camera_open:
            self.camera.close()
            self._is_camera_open = False

    def take_photo(self):
        stream = io.BytesIO()
        # with open('temp.jpg', 'rb') as f:
        #     data = f.read()
        self.camera.capture(stream, format='jpeg')
        stream.seek(0)
        # data = io.BytesIO(data)
        return stream.read(), np.asarray(Image.open(stream))

    @staticmethod
    def is_active_schedule():
        schedules = get_schedules()
        date_now = datetime.now()
        for schedule in schedules:
            week_ok = schedule.weekday == Schedules.WEEKDAYS[date_now.weekday()] or schedule.weekday == Schedules.All
            time_ok = schedule.start_time <= date_now.time() <= schedule.end_time
            if week_ok and time_ok:
                return True
        return False

    def broadcast_photo(self, photo_data: bytes, photo_array: np.ndarray):
        image_date = datetime.now()
        if self._image_manager.is_image_new(photo_array):  # Send it to storage server
            server_uploader.send_image(image_data=photo_data, image_date=image_date)
        if self._image_manager.is_image_suspicious(photo_array):
            for chat_id in get_subscribers():  # Send it to subscribers
                try:
                    send_image(chat_id=chat_id, image_data=photo_data, caption=image_date.strftime('%d/%m/%Y %H:%M:%S'))
                except Exception as e:
                    logging.exception(e)
        self._image_manager.next_image(photo_array)

    def start_watching(self):
        while True:
            if self.is_active_schedule():
                try:
                    self._open_camera()
                    photo_data, photo_array = self.take_photo()
                    self.broadcast_photo(photo_data=photo_data, photo_array=photo_array)
                except Exception as e:
                    logging.error("Can't take image or broadcast it. Please check the error bellow.")
                    logging.exception(e)
            else:
                self._image_manager.clear()
                self._close_camera()
            time.sleep(2)


cctv = CCTV()
