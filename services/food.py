from sqlalchemy import func, desc

from database import db_session
from models.user import User
from models.food import Food

from error_handling.generic_error import GenericError


def log_food(user_name, food_type, title, timestamp, score, picture, grams):
    try:
        user = db_session.query(User).filter(User.user_name == user_name.lower()).first()

        food = Food(user.id, food_type.lower(), title, timestamp, score, str(picture), grams)
        db_session.add(food)
        db_session.flush()
        return {"message": "Success", "food": food.get_dict()}
    except Exception as e:
        raise GenericError(e.message)
    except:
        raise GenericError("Unspecific error came up")


def get_most_frequent_food(user_name):
    user = db_session.query(User).filter(User.user_name == user_name).first()

    foods = db_session.query(func.count(Food.id).label('qty'), Food.title).filter(Food.user_id == user.id).group_by(
        Food.title).order_by(desc('qty')).limit(3)

    all_foods = []
    order = 0
    for food in foods:
        food_object = db_session.query(Food).filter(Food.title == food[1]).filter(Food.picture is not None).first()
        if food_object is None:
            food_object = db_session.query(Food).filter(Food.title == food[1]).first()
        food_dict = food_object.get_dict()
        food_dict['order'] = order
        food_dict['title'] = food_dict['title'].encode("UTF-8")
        all_foods.append(food_dict)
        order += 1
    return all_foods


def delete_food(user_name, food_id):
    try:
        user = db_session.query(User).filter(User.user_name == user_name).first()
        food = db_session.query(Food).filter(Food.id == food_id).filter(Food.user_id == user.id).one()

        db_session.delete(food)
        db_session.flush()
        return {"message": "Success"}
    except Exception as e:
        raise GenericError(e.message)
    except:
        raise GenericError("Unspecific error came up")


def edit_food(user_name, food_id, food_type, title, timestamp, score, picture, grams):
    try:
        user = db_session.query(User).filter(User.user_name == user_name.lower()).first()

        food = db_session.query(Food).filter(Food.id == food_id).filter(Food.user_id == user.id).one()
        food.grams = grams
        food.picture = picture
        food.score = score
        if timestamp is not None:
            food.timestamp = timestamp
        food.title = title
        food.type = food_type

        db_session.flush()
        return {"message": "Success", "food": food.get_dict()}
    except Exception as e:
        raise GenericError(e.message)
    except:
        raise GenericError("Unspecific error came up")
