from models.user import User

from database import db_session


def login(user_name):
    user_name = user_name.lower()
    user = db_session.query(User).filter(User.user_name == user_name).first()

    if user is not None:
        return {'message': 'success', 'user': user.get_dict()}

    else:
        return {'message': 'user does not exist', 'user': None}
