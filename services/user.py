import datetime

from models.activity import Activity
from models.food import Food
from models.user import User

from database import db_session

from sqlalchemy import func


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
    print date_obj.date()

    objects_for_timeline = []
    foods = db_session.query(Food).filter(Food.user_id == user.id).filter(
        func.extract('year', Food.timestamp) == date_obj.date())
    print foods
    activities = db_session.query(Activity).filter(Activity.user_id == user.id).filter(
        func.extract(Activity.start_time, 'date') == date_obj.date())

    for food in foods:
        objects_for_timeline.append(food.get_dict())

    for activity in activities:
        objects_for_timeline.append(activity.get_dict())

    return objects_for_timeline
