from datetime import date
import ast

from database import db_session
#from models.user import User
#from models.food import Food

from error_handling.generic_error import GenericError
import fitbit
from fitbit.api import FitbitOauth2Client

from models.user import User


def get_sleep_from_fitbit(date_string):
    try:
        user = db_session.query(User).filter(User.user_name == "finnur").first()
        access_token_all = ast.literal_eval(user.fitbit_access_token)
        access_token = access_token_all['access_token']
        server = fitbit.Fitbit(client_id='227PT7', client_secret='52d59408469ac8aa82d4bdcca69071a6', access_token=access_token)
        date_obj = date(*map(int, date_string.split('-')))
        print date_obj
        return server.get_sleep(date_obj)
        #return {"message": "Success", "food": food.get_dict()}
    except Exception as e:
        raise GenericError(e.message)
    except:
        raise GenericError("Unspecific error came up")