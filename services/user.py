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

from sqlalchemy import func, Date, cast, and_

from services.notification import send_notification
from services.sleep import get_sleep_for_day
from services.time_calculations import perdelta_time, seconds_to_hours_minutes_verbal, perdelta

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
    output.headers["Content-Disposition"] = "attachment; filename=" + type + ".csv"
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

    return create_csv_string(sleep_objects, user_name + "_sleeps")


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

    return create_csv_string(food_objects, user_name + "_foods")


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
        dict_for_export['start_time'] = str(activity.start_time.strftime("%H:%M"))
        dict_for_export['end_time'] = str(activity.end_time.strftime("%H:%M"))
        dict_for_export['date'] = str(activity.start_time.strftime("%Y-%m-%d"))
        activities_objects.append(dict_for_export)

    return create_csv_string(activities_objects, user_name + "_activities")


def sleep_prediction(user_name, today_date_obj=None):
    if today_date_obj == None:
        today_date_obj = datetime.datetime.today()
    else:
        today_date_obj = datetime.datetime.strptime(today_date_obj, "%Y-%m-%d")
    user = db_session.query(User).filter(User.user_name == user_name).first()

    today_activities = db_session.query(Activity).filter(Activity.user_id == user.id).filter(
        and_(func.date_part('year', Activity.start_time) == today_date_obj.date().year,
             func.date_part('month', Activity.start_time) == today_date_obj.date().month,
             func.date_part('day', Activity.start_time) == today_date_obj.date().day))

    today_foods = db_session.query(Food).filter(Food.user_id == user.id).filter(
        and_(func.date_part('year', Food.timestamp) == today_date_obj.date().year,
             func.date_part('month', Food.timestamp) == today_date_obj.date().month,
             func.date_part('day', Food.timestamp) == today_date_obj.date().day))

    print today_activities.first()
    today_activities_ids = [activity.id for activity in today_activities.all()]
    today_foods_ids = [food.id for food in today_foods.all()]

    activities = db_session.query(Activity).filter(Activity.user_id == user.id).filter(
        Activity.id.notin_(today_activities_ids))

    print activities.first()

    foods = db_session.query(Food).filter(Food.user_id == user.id).filter(Food.id.notin_(today_foods_ids))

    activities_objects = {}
    for activity in activities:
        dict_for_prediction = activity.get_dict_for_export()
        time_difference = activity.end_time - activity.start_time
        dict_for_prediction['duration_seconds'] = time_difference.total_seconds()
        dict_for_prediction['date'] = str(activity.start_time.strftime("%Y-%m-%d"))
        print dict_for_prediction
        if dict_for_prediction['date'] in activities_objects:
            activities_objects[dict_for_prediction['date']].append(dict_for_prediction)
        else:
            activities_objects[dict_for_prediction['date']] = [dict_for_prediction]

    today_sum_activities_duration = 0.0
    count = 0
    today_activities_average_per_day = 0.0
    for activity in today_activities:
        dict_for_prediction = activity.get_dict_for_export()
        time_difference = activity.end_time - activity.start_time
        today_sum_activities_duration += time_difference.total_seconds()
        count += 1

    if count > 0:
        today_activities_average_per_day = float(today_sum_activities_duration / count)


    foods_objects = {}
    for food in foods:
        dict_for_prediction = food.get_dict_for_export()
        dict_for_prediction['date'] = str(food.timestamp.date())

        if dict_for_prediction['date'] in foods_objects:
            foods_objects[dict_for_prediction['date']].append(dict_for_prediction)
        else:
            foods_objects[dict_for_prediction['date']] = [dict_for_prediction]

    today_sum_foods_score = 0.0
    today_foods_average_per_day = 0.0
    count = 0
    for food in today_foods:
        dict_for_prediction = food.get_dict_for_export()
        today_sum_foods_score += dict_for_prediction['score']
        count += 1

    if count > 0:
        today_foods_average_per_day = float(today_sum_foods_score / count)

    activites_average_per_day = {}
    foods_average_per_day = {}

    count = 0
    for date_result in perdelta(datetime.datetime(2016, 04, 01), datetime.datetime.today(),
                                datetime.timedelta(days=1)):
        if date_result.date != today_date_obj.date():
            date_str = date_result.strftime("%Y-%m-%d")
            print date_str
            print date_result
            print activities_objects
            if date_str in activities_objects:
                activites_average_per_day[count] = float(
                    sum(d['duration_seconds'] for d in activities_objects[date_str])) / len(
                    activities_objects[date_str])
            if date_str in foods_objects:
                foods_average_per_day[count] = float(sum(d['score'] for d in foods_objects[date_str])) / len(
                    foods_objects[date_str])
            count += 1

    print activites_average_per_day
    print today_activities_average_per_day
    closest_activity_day = min(activites_average_per_day, key=lambda x: abs(x - today_activities_average_per_day))
    closest_food_day = min(foods_average_per_day, key=lambda x: abs(x - today_foods_average_per_day))

    count = 0
    activity_efficiency = 0.0
    food_efficiency = 0.0
    for date_result in perdelta(datetime.datetime(2016, 04, 01), datetime.datetime.today(),
                                datetime.timedelta(days=1)):
        if date_result.date != today_date_obj.date():
            if count == closest_activity_day:
                activity_efficiency = get_efficiency_average_of_sleep(user.id, date_result)

            if count == closest_food_day:
                food_efficiency = get_efficiency_average_of_sleep(user.id, date_result)
            count += 1

    if activity_efficiency == 0:
        return food_efficiency
    elif food_efficiency == 0:
        return activity_efficiency

    return 0.8 * activity_efficiency + 0.2 * food_efficiency


def get_efficiency_average_of_sleep(user_id, date_obj):
    sleeps = db_session.query(Sleep).filter(Sleep.user_id == user_id).filter(
        Sleep.date_of_sleep == str(date_obj.date()+datetime.timedelta(days=1)))

    no_of_logs = 0
    efficiency = 0
    for sleep in sleeps:
        sleep_data = sleep.get_dict()
        no_of_logs += 1
        efficiency += sleep_data['efficiency']

    if no_of_logs > 0:
        return float(efficiency / no_of_logs)
    else:
        return 0.0
