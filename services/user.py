import StringIO
import datetime
import os
from operator import itemgetter

from flask import make_response

from models.activity import Activity
from models.food import Food
from models.sleep import Sleep
from models.user import User

from database import db_session

from sqlalchemy import func, Date, cast

from services.notification import send_notification
from services.sleep import get_sleep_for_day
from services.time_calculations import perdelta_time, seconds_to_hours_minutes_verbal

import csv


def login(user_name):
    user_name = user_name.lower()
    user = db_session.query(User).filter(User.user_name == user_name).first()

    if user is not None:
        return {'message': 'success', 'user': user.get_dict()}

    else:
        return {'message': 'user does not exist', 'user': None}


def get_timeline(user_name, date_str):
    user = db_session.query(User).filter(User.user_name == user_name).first()

    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")

    objects_for_timeline = []
    foods = db_session.query(Food).filter(Food.user_id == user.id).filter(
        func.date_part('year', Food.timestamp) == date_obj.date().year).filter(
        func.date_part('month', Food.timestamp) == date_obj.date().month).filter(
        func.date_part('day', Food.timestamp) == date_obj.date().day)

    activities = db_session.query(Activity).filter(Activity.user_id == user.id).filter(
        func.date_part('year', Activity.start_time) == date_obj.date().year).filter(
        func.date_part('month', Activity.start_time) == date_obj.date().month).filter(
        func.date_part('day', Activity.start_time) == date_obj.date().day)

    for food in foods:
        food_dict = food.get_dict()
        food_dict['type'] = 'food'
        food_dict['date'] = str(food.timestamp.date())
        food_dict['time'] = str(food.timestamp.time())
        objects_for_timeline.append(food_dict)

    for activity in activities:
        activity_dict = activity.get_dict()
        activity_dict['type'] = 'activity'
        activity_dict['date'] = str(activity.start_time.strftime("%Y-%m-%d"))
        activity_dict['time'] = str(activity.start_time.strftime("%H:%M"))
        time_difference = activity.end_time - activity.start_time
        # print time_difference.total_seconds()
        duration = seconds_to_hours_minutes_verbal(time_difference.total_seconds())
        # print duration
        activity_dict['duration'] = duration.strip()
        objects_for_timeline.append(activity_dict)

    sorted_object_for_timeline = sorted(objects_for_timeline, key=itemgetter('time'))

    return sorted_object_for_timeline


def send_notifications_if_not_records_today():
    users = db_session.query(User)

    remind_users = []
    for user in users:
        foods = db_session.query(Food).filter(Food.user_id == user.id).filter(
            cast(Food.timestamp, Date) == datetime.date.today())
        activities = db_session.query(Activity).filter(Activity.user_id == user.id).filter(
            cast(Activity.start_time, Date) == datetime.date.today())

        if foods == None and activities == None:
            remind_users.append(user.id)

    send_notification("Remember to log your children's foods and activities every day!", remind_users)


def create_csv_string(list_of_dicts, type):
    keys = list_of_dicts[0].keys()
    si = StringIO.StringIO()
    dict_writer = csv.DictWriter(si, keys)
    dict_writer.writeheader()
    dict_writer.writerows(list_of_dicts)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename="+type+".csv"
    output.headers["Content-type"] = "text/csv"
    return output


def export_sleep(user_name):
    if user_name != None:
        user = db_session.query(User).filter(User.user_name == user_name).first()

        sleeps = db_session.query(Sleep).filter(Sleep.user_id == user.id)
    else:
        sleeps = db_session.query(Sleep)
        user_name = "all"

    sleep_objects = []
    for sleep in sleeps:
        dict_for_export = sleep.get_data_for_export()
        dict_for_export['time'] = str(sleep.start_time.strftime("%H:%M"))
        dict_for_export['date'] = str(sleep.start_time.strftime("%Y-%m-%d"))
        sleep_objects.append(dict_for_export)

    return create_csv_string(sleep_objects, user_name+"_sleeps")


def export_food(user_name):
    if user_name != None:
        user = db_session.query(User).filter(User.user_name == user_name).first()

        foods = db_session.query(Food).filter(Food.user_id == user.id)
    else:
        foods = db_session.query(Food)
        user_name = "all"

    food_objects = []
    for food in foods:
        dict_for_export = food.get_dict_for_export()
        dict_for_export['time'] = str(food.timestamp.time())
        dict_for_export['date'] = str(food.timestamp.date())
        food_objects.append(dict_for_export)

    return create_csv_string(food_objects, user_name+"_foods")


def export_activities(user_name):
    if user_name != None:
        user = db_session.query(User).filter(User.user_name == user_name).first()

        activities = db_session.query(Activity).filter(Activity.user_id == user.id)
    else:
        activities = db_session.query(Activity)
        user_name = "all"

    activities_objects = []
    for activity in activities:
        dict_for_export = activity.get_dict_for_export()
        time_difference = activity.end_time - activity.start_time
        dict_for_export['duration_seconds'] = time_difference.total_seconds()
        dict_for_export['time'] = str(activity.start_time.strftime("%H:%M"))
        dict_for_export['date'] = str(activity.start_time.strftime("%Y-%m-%d"))
        activities_objects.append(dict_for_export)

    return create_csv_string(activities_objects, user_name+"_activities")




