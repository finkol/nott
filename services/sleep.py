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

from models.sleep import Sleep
from models.user import User
import requests


def get_new_refresh_token(client_id, client_secret, refresh_token):
    url = 'https://api.fitbit.com/oauth2/token'
    unenc_str = (client_id + ':' + client_secret).encode('utf8')
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Authorization': b'Basic ' + base64.b64encode(unenc_str)
    }

    payload = {'grant_type': 'refresh_token', 'refresh_token': refresh_token}

    r = requests.post(url, headers=headers, data=payload)
    return str(r.content)


def get_sleep_from_fitbit(user_name, dates):
    try:
        user = db_session.query(User).filter(User.user_name == user_name).first()
        token = ast.literal_eval(user.fitbit_access_token)
        #access_token = token['access_token']
        refresh_token = token['refresh_token']

        token = get_new_refresh_token('227PT7', '52d59408469ac8aa82d4bdcca69071a6', refresh_token)
        if 'access_token' in token:
            user.fitbit_access_token = str(token)
            db_session.flush()

            token = ast.literal_eval(token)

        server = fitbit.Fitbit(client_id='227PT7', client_secret='52d59408469ac8aa82d4bdcca69071a6',
                               access_token=token['access_token'], refresh_token=token['refresh_token'])

        sleep = []
        for one_date in dates:
            sleep_fitbit_object = server.get_sleep(one_date)
            if sleep_fitbit_object is not None:
                sleep_db_object = db_session.query(Sleep).filter(Sleep.log_id == str(sleep_fitbit_object['sleep'][0]['logId'])).first()
                if sleep_db_object is None:
                    sleep_object = Sleep()

                    sleep_object.log_id = str(sleep_fitbit_object['sleep'][0]['logId'])
                    sleep_object.awake_count = sleep_fitbit_object['sleep'][0]['awakeCount']
                    sleep_object.awake_duration = sleep_fitbit_object['sleep'][0]['awakeDuration']
                    sleep_object.date_of_sleep = sleep_fitbit_object['sleep'][0]['dateOfSleep']
                    sleep_object.duration = sleep_fitbit_object['sleep'][0]['duration']
                    sleep_object.efficiency = sleep_fitbit_object['sleep'][0]['efficiency']
                    sleep_object.is_main_sleep = sleep_fitbit_object['sleep'][0]['isMainSleep']
                    sleep_object.minutes_after_wakeup = sleep_fitbit_object['sleep'][0]['minutesAfterWakeup']
                    sleep_object.minutes_awake = sleep_fitbit_object['sleep'][0]['minutesAwake']
                    sleep_object.minutes_asleep = sleep_fitbit_object['sleep'][0]['minutesAsleep']
                    sleep_object.restless_count = sleep_fitbit_object['sleep'][0]['restlessCount']
                    sleep_object.restless_duration = sleep_fitbit_object['sleep'][0]['restlessDuration']
                    sleep_object.start_time = sleep_fitbit_object['sleep'][0]['startTime']
                    sleep_object.time_in_bed = sleep_fitbit_object['sleep'][0]['timeInBed']
                    sleep_object.minute_data = str(sleep_fitbit_object['sleep'][0]['minuteData'])
                    sleep_object.user_id = user.id
                    sleep_object.minutes_to_fall_asleep = sleep_fitbit_object['sleep'][0]['minutesToFallAsleep']

                    db_session.add(sleep_object)
                    db_session.flush()

                sleep.append(sleep_fitbit_object)

        return sleep
    except Exception as e:
        raise GenericError(e.message)
    except:
        raise GenericError("Unspecific error came up")