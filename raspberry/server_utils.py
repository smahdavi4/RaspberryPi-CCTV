import io
import logging
import urllib.parse
import requests
from datetime import datetime


class ServerUploader:
    def __init__(self):
        self.bot_token = None
        self.server_address = None

    def initialize(self, bot_token: str, server_address: str):
        self.bot_token = bot_token
        self.server_address = server_address

    def send_image(self, image_data: io.BytesIO, image_date: datetime):
        try:
            response = requests.post(

                url=urllib.parse.urljoin(self.server_address, f"upload/{self.bot_token}"),
                files={
                    'image': image_data
                },
                data={
                    'date': image_date.strftime('%d/%m/%Y %H:%M:%S')
                }
            )
        except Exception as e:
            logging.exception(e)
            return False

        if 200 <= response.status_code < 400:
            return True
        else:
            logging.error(f"Error Sending Image. Details: status_code={response.status_code}, body={response.text}.")
            return False


server_uploader = ServerUploader()
