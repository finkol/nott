from datetime import datetime, timedelta
from sqlalchemy import func, desc

from database import db_session
from error_handling.generic_error import GenericError
from models.user import User
from models.activity import Activity
from services.time_calculations import perdelta, seconds_to_hours_minutes


def log_activity(user_name, activity_type, start_time, end_time):
    try:
        user = db_session.query(User).filter(User.user_name == user_name).first()
        print user.id
        activity = Activity(user.id, activity_type, start_time, end_time)
        db_session.add(activity)
        db_session.flush()
        return {"message": "Success", "activity": activity.get_dict()}
    except Exception as e:
        raise GenericError(e.message)
    except:
        raise GenericError("Unspecific error came up")


def get_most_frequent_activity(user_name):
    user = db_session.query(User).filter(User.user_name == user_name).first()

    activities = db_session.query(func.count(Activity.id).label('qty'), Activity.activity_type).filter(
        Activity.user_id == user.id).group_by(
        Activity.activity_type).order_by(desc('qty')).limit(3)

    all_activities = []
    for activity in activities:
        print activity[1]
        activity_object = db_session.query(Activity).filter(Activity.activity_type == activity[1]).first()
        all_activities.append(activity_object.get_dict())

    return all_activities


def get_device_usage_chart(user_name):
    user = db_session.query(User).filter(User.user_name == user_name).first()

    activities_duration = []
    for result in perdelta(datetime(2016, 04, 01), datetime.today(),
                           timedelta(days=1)):
        activities = db_session.query(Activity).filter(Activity.user_id == user.id).filter(
            func.date_part('year', Activity.start_time) == result.date().year).filter(
            func.date_part('month', Activity.start_time) == result.date().month).filter(
            func.date_part('day', Activity.start_time) == result.date().day)

        iPhone_duration = 0
        iPad_duration = 0
        tv_duration = 0
        other_duration = 0
        for activity in activities:
            duration = abs((activity.end_time - activity.start_time).seconds)

            if activity.activity_type == "iPhone":
                iPhone_duration += duration

            elif activity.activity_type == "iPad":
                iPad_duration += duration

            elif activity.activity_type == "TV":
                tv_duration += duration

            else:
                other_duration += duration

        activities_on_this_day = dict(date=str(result.date()), iPhone_duration=seconds_to_hours_minutes(iPhone_duration),
                                      iPad_duration=seconds_to_hours_minutes(iPad_duration),
                                      tv_duration=seconds_to_hours_minutes(tv_duration),
                                      other_duration=seconds_to_hours_minutes(other_duration))

        activities_duration.append(activities_on_this_day)

    return activities_duration
