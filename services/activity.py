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

