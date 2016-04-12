import base64
from datetime import date
import ast

from database import db_session
#from models.user import User
#from models.food import Food

from error_handling.generic_error import GenericError
import fitbit
from fitbit.api import FitbitOauth2Client

import json

from models.user import User
import requests


def get_new_refresh_token(client_id, client_secret, access_token, refresh_token):
    url = 'https://api.fitbit.com/oauth2/token'
    unenc_str = (client_id + ':' + client_secret).encode('utf8')
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Authorization': b'Basic ' + base64.b64encode(unenc_str)
    }

    payload = {'grant_type': 'refresh_token', 'refresh_token': refresh_token}

    r = requests.post(url, headers=headers, data=payload)
    return str(r.content)


def get_sleep_from_fitbit(user_name, date_string):
    #try:
    user = db_session.query(User).filter(User.user_name == user_name).first()
    token = ast.literal_eval(user.fitbit_access_token)
    access_token = token['access_token']
    refresh_token = token['refresh_token']

    token = get_new_refresh_token('227PT7', '52d59408469ac8aa82d4bdcca69071a6', ' ', refresh_token)
    user.fitbit_access_token = str(token)
    db_session.flush()

    token = ast.literal_eval(token)

    server = fitbit.Fitbit(client_id='227PT7', client_secret='52d59408469ac8aa82d4bdcca69071a6',
                           access_token=token['access_token'], refresh_token=token['refresh_token'])

    date_obj = date(*map(int, date_string.split('-')))
    print date_obj
    return server.get_sleep(date_obj)
    #except Exception as e:
     #   raise GenericError(e.message)
    #except:
    #    raise GenericError("Unspecific error came up")