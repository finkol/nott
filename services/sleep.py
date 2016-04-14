import base64
from datetime import date, timedelta, time, datetime
import ast

from database import db_session
# from models.user import User
# from models.food import Food

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
    # try:
    user = db_session.query(User).filter(User.user_name == user_name).first()
    token = ast.literal_eval(user.fitbit_access_token)
    # access_token = token['access_token']
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
        sleep_fitbit_objects = server.get_sleep(one_date)
        # print sleep_fitbit_objects
        print len(sleep_fitbit_objects['sleep'])
        if len(sleep_fitbit_objects['sleep']) > 0:
            i = 0
            for sleep_fitbit_object in sleep_fitbit_objects['sleep']:
                print sleep_fitbit_object
                sleep_db_object = db_session.query(Sleep).filter(
                    Sleep.log_id == str(sleep_fitbit_object['logId'])).first()
                if sleep_db_object is None:
                    sleep_object = Sleep()

                    sleep_object.log_id = str(sleep_fitbit_object['logId'])
                    sleep_object.awake_count = sleep_fitbit_object['awakeCount']
                    sleep_object.awake_duration = sleep_fitbit_object['awakeDuration']
                    sleep_object.date_of_sleep = sleep_fitbit_object['dateOfSleep']
                    sleep_object.duration = sleep_fitbit_object['duration']
                    sleep_object.efficiency = sleep_fitbit_object['efficiency']
                    sleep_object.is_main_sleep = sleep_fitbit_object['isMainSleep']
                    sleep_object.minutes_after_wakeup = sleep_fitbit_object['minutesAfterWakeup']
                    sleep_object.minutes_awake = sleep_fitbit_object['minutesAwake']
                    sleep_object.minutes_asleep = sleep_fitbit_object['minutesAsleep']
                    sleep_object.restless_count = sleep_fitbit_object['restlessCount']
                    sleep_object.restless_duration = sleep_fitbit_object['restlessDuration']
                    sleep_object.start_time = sleep_fitbit_object['startTime']
                    sleep_object.time_in_bed = sleep_fitbit_object['timeInBed']
                    sleep_object.minute_data = str(sleep_fitbit_object['minuteData'])
                    sleep_object.user_id = user.id
                    sleep_object.minutes_to_fall_asleep = sleep_fitbit_object['minutesToFallAsleep']

                    db_session.add(sleep_object)
                    db_session.flush()
                    i += 1

                sleep.append(sleep_fitbit_object)

    return sleep
    # except Exception as e:
    #    raise GenericError(e.message)
    # except:
    #    raise GenericError("Unspecific error came up")


def time_plus(time, timedelta):
    start = datetime(
        2000, 1, 1,
        hour=time.hour, minute=time.minute, second=time.second)
    end = start + timedelta
    return end.time()


def perdelta(start, end, delta):
    curr = start
    while curr != end:
        yield curr
        curr = time_plus(curr, delta)


def minutes_to_hours_minutes(minutes):
    minutes = timedelta(minutes=minutes)
    d = datetime(1, 1, 1) + minutes

    return "%02d:%02d" % (d.hour, d.minute)


def get_sleep_for_day(user_name, date_str):
    user = db_session.query(User).filter(User.user_name == user_name).first()
    sleeps = db_session.query(Sleep).filter(Sleep.user_id == user.id).filter(Sleep.date_of_sleep == date_str)

    night_minute_interval = {}
    for result in perdelta(time(19, 0, 0), time(10, 0, 0), timedelta(minutes=1)):
        # interval_instance = {'time': str(result), 'value': 4}
        night_minute_interval[str(result)] = "out of bed"

    sleeps_list = []
    sleep_summary = {}
    asleep_minutes = 0
    awake_minutes = 0
    really_awake_minutes = 0
    no_of_logs = 0
    efficiency = 0
    start_time = ""
    end_time = ""

    for sleep in sleeps:
        sleep_data = sleep.get_dict()
        sleeps_list.append(sleep_data)
        for minute_data in sleep_data['minute_data']:
            if minute_data['value'] == "1":
                night_minute_interval[minute_data['dateTime']] = "asleep"
                asleep_minutes += 1
            elif minute_data['value'] == "2":
                night_minute_interval[minute_data['dateTime']] = "awake"
                awake_minutes += 1
            elif minute_data['value'] == "3":
                night_minute_interval[minute_data['dateTime']] = "really awake"
                really_awake_minutes += 1
            end_time = minute_data['dateTime']
        no_of_logs += 1
        efficiency += sleep_data['efficiency']
        if no_of_logs == 1:
            start_time = sleep_data['start_time']

    start_time = start_time.split()[1]
    time_summary = {'asleep': minutes_to_hours_minutes(asleep_minutes),
                    'awake': minutes_to_hours_minutes(awake_minutes),
                    'really_awake_minutes': minutes_to_hours_minutes(really_awake_minutes),
                    'start_time': start_time,
                    'end_time': end_time}

    sleep_summary = {'efficiency': float(efficiency/no_of_logs), 'date_of_sleep': date_str}

    return dict(night_minute_interval=night_minute_interval, time_summary=time_summary, sleep_summary=sleep_summary)
