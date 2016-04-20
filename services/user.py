import datetime
from operator import itemgetter

from models.activity import Activity
from models.food import Food
from models.user import User

from database import db_session

from sqlalchemy import func

from services.time_calculations import perdelta_time, seconds_to_hours_minutes_verbal


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
        #print time_difference.total_seconds()
        duration = seconds_to_hours_minutes_verbal(time_difference.total_seconds())
        #print duration
        activity_dict['duration'] = duration.strip()
        objects_for_timeline.append(activity_dict)

    sorted_object_for_timeline = sorted(objects_for_timeline, key=itemgetter('time'))

    return sorted_object_for_timeline
