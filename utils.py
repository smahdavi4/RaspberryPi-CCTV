import logging
import random

from peewee import DoesNotExist

from models import Users


def _generate_password():
    return str(random.randint(10000, 99999))


def create_user(chat_id):
    try:
        user = Users.get(Users.chat_id == str(chat_id))
        if user.is_active:
            return None
        else:
            user.otp = _generate_password()
            user.save()
            return user.otp
    except DoesNotExist:
        user = Users.create(chat_id=chat_id, otp=_generate_password())
        return user.otp


def activate_user(chat_id, passwd):
    try:
        user = Users.get(Users.chat_id == str(chat_id))
        if passwd == user.otp:
            user.is_active = True
            user.save()
            return True, None
        else:
            user.otp = _generate_password()
            user.save()
            return False, user.otp
    except DoesNotExist as e:
        logging.error(e)
        return False, None


def is_user_active(chat_id):
    chat_id = str(chat_id)
    try:
        user = Users.get(Users.chat_id == chat_id)
        return user.is_active
    except DoesNotExist as e:
        logging.error(e)
        return False


def delete_user(chat_id):
    chat_id = str(chat_id)
    try:
        Users.get(Users.chat_id == chat_id).delete_instance()
    except DoesNotExist as e:
        logging.exception(e)
        raise e
