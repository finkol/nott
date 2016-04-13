from sqlalchemy import func, desc

from database import db_session
from error_handling.generic_error import GenericError
from models.user import User
from models.activity import Activity


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
