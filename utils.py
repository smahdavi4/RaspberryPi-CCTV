import logging
import random
import time

from peewee import DoesNotExist

from models import Users, Schedules


def _generate_password():
    return str(random.randint(10000, 99999))


def is_time_format(inp):
    try:
        time.strptime(inp, '%H:%M')
        return True
    except ValueError:
        return False


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
        logging.exception(e)
        return False, None


def is_user_active(chat_id):
    chat_id = str(chat_id)
    try:
        user = Users.get(Users.chat_id == chat_id)
        return user.is_active
    except DoesNotExist as e:
        logging.error(e)
        return False


def get_subscribers():
    active_users = list(Users.select().where(Users.is_active == True))
    chat_ids = [user.chat_id for user in active_users]
    return chat_ids


def delete_user(chat_id):
    chat_id = str(chat_id)
    try:
        Users.get(Users.chat_id == chat_id).delete_instance()
    except DoesNotExist as e:
        logging.exception(e)
        raise e


def create_schedule(start_time: str, end_time: str, weekday: str):
    weekday = weekday.capitalize()
    if weekday not in Schedules.WEEKDAYS:
        raise Exception("Weekday invalid")
    elif not is_time_format(start_time) or not is_time_format(end_time):
        raise Exception("Start/End Time invalid")
    else:
        Schedules.create(weekday=weekday, start_time=start_time, end_time=end_time)


def delete_schedule(schedule_id):
    try:
        Schedules.get(Schedules.id == schedule_id).delete_instance()
    except DoesNotExist as e:
        logging.exception(e)
        raise e


def get_schedules():
    schedules = list(Schedules.select())
    return schedules
