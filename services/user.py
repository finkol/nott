import datetime
import os
from operator import itemgetter

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
        food_dict['time'] = str(food.timestamp.time())
        objects_for_timeline.append(food_dict)

    for activity in activities:
        activity_dict = activity.get_dict()
        activity_dict['type'] = 'activity'
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
            cast(Food.date_time, Date) == datetime.date.today())
        activities = db_session.query(Activity).filter(Activity.user_id == user.id).filter(
            cast(Activity.start_time, Date) == datetime.date.today())

        if foods == None and activities == None:
            remind_users.append(user.id)

    send_notification("Remember to log your children's foods and activities every day!", remind_users)


def create_csv_string(list_of_dicts):
    #Create a master list of keys
    allKeys = list_of_dicts[0].keys()

    whole_string = ','.join(allKeys) + os.linesep
    #Go through printing the rows
    for row in list_of_dicts:
        values = []
        line_string = ""
        for key in allKeys:
            #Add the values if it exists, if no key in this row add a blank
            if key in row:
                values.append(str(row[key]))
            else:
                values.append('')
        line_string = ','.join(values)
        whole_string += line_string + os.linesep

    return whole_string

def export_food(user_name, date_str):
    user = db_session.query(User).filter(User.user_name == user_name).first()
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    date_str_plus_one = (date_obj + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    foods = db_session.query(Food).filter(Food.user_id == user.id).filter(
        cast(Food.timestamp, Date) == date_obj)
    activities = db_session.query(Activity).filter(Activity.user_id == user.id).filter(
        cast(Activity.start_time, Date) == date_obj)
    sleeps = get_sleep_for_day(user_name, date_str_plus_one)

    food_objects = []
    for food in foods:
        food_objects.append(food.get_dict_without_picture())

    activities_objects = []
    for activity in activities:
        activities_objects.append(activity.get_dict())

    return dict(sleep_summary=sleeps['sleep_summary'], sleep_time_summary=sleeps['time_summary'], foods=food_objects, activities=activities_objects)

def export_activities(user_name, date_str):
    user = db_session.query(User).filter(User.user_name == user_name).first()
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    date_str_plus_one = (date_obj + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    activities = db_session.query(Activity).filter(Activity.user_id == user.id).filter(
        cast(Activity.start_time, Date) == date_obj)

    activities_objects = []
    for activity in activities:
        activities_objects.append(activity.get_dict())

    return create_csv_string(activities_objects)




