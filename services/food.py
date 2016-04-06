from database import db_session
from models.user import User
from models.food import Food

from error_handling.generic_error import GenericError


def log_food(user_name, food_type, title, timestamp, score, picture, grams):
    try:
        user = db_session.query(User).filter(User.user_name == user_name).first()

        food = Food(user.id,food_type, title, timestamp, score, str(picture), grams)
        db_session.add(food)
        db_session.flush()
        return {"message": "Success", "food": food.get_dict()}
    except Exception as e:
        raise GenericError(e.message)
    except:
        raise GenericError("Unspecific error came up")


