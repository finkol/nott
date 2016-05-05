import ast
from datetime import timedelta, time, datetime

import fitbit

from database import db_session
from error_handling.generic_error import GenericError
from models.sleep import Sleep
from models.user import User
from services.fitbit_services.fitbit_api import get_new_refresh_token
from services.time_calculations import perdelta_time, perdelta, minutes_to_hours_minutes

epoch = datetime.utcfromtimestamp(0)


def get_sleep_from_fitbit(user_name, dates):
    try:
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
            if len(sleep_fitbit_objects['sleep']) > 0:
                i = 0
                for sleep_fitbit_object in sleep_fitbit_objects['sleep']:
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
    except Exception as e:
        raise GenericError(e.message)
    except:
        raise GenericError("Unspecific error came up")


def get_sleep_for_day(user_name, date_str):
    user = db_session.query(User).filter(User.user_name == user_name).first()
    sleeps = db_session.query(Sleep).filter(Sleep.user_id == user.id).filter(Sleep.date_of_sleep == date_str)

    last_data = ""
    last_date_time = ""

    night_minute_interval = {}
    number_of_minutes = 0.0
    for result in perdelta_time(time(18, 0, 0), time(10, 0, 0), timedelta(minutes=1)):
        # night_minute_interval[str(result)] = "out of bed"
        number_of_minutes += 1.0

    sleeps_list = []
    asleep_minutes = 0
    awake_minutes = 0
    really_awake_minutes = 0
    no_of_logs = 0
    efficiency = 0
    start_time = ""
    end_time = ""

    interval_start_time = ""
    interval_end_time = ""
    interval_type = ""
    interval_objects = []

    for sleep in sleeps:
        sleep_data = sleep.get_dict()
        sleeps_list.append(sleep_data)
        for minute_data in sleep_data['minute_data']:
            if minute_data['value'] == "1":
                if last_data != "asleep":
                    interval_end_time = last_date_time

                    if interval_start_time != "" and interval_end_time != "":
                        interval_objects.append(
                            dict(start_time=interval_start_time, end_time=interval_end_time, type=interval_type))

                    interval_start_time = minute_data['dateTime']
                    interval_type = "asleep"

                    night_minute_interval[minute_data['dateTime']] = "asleep"
                    night_minute_interval[last_date_time] = last_data
                asleep_minutes += 1
                last_data = "asleep"
                last_date_time = minute_data['dateTime']

            elif minute_data['value'] == "2":
                if last_data != "awake":
                    interval_end_time = last_date_time
                    if interval_start_time != "" and interval_end_time != "":
                        interval_objects.append(
                            dict(start_time=interval_start_time, end_time=interval_end_time, type=interval_type))

                    interval_start_time = minute_data['dateTime']
                    interval_type = "awake"

                    night_minute_interval[minute_data['dateTime']] = "awake"
                    night_minute_interval[last_date_time] = last_data
                awake_minutes += 1
                last_data = "awake"
                last_date_time = minute_data['dateTime']

            elif minute_data['value'] == "3":
                if last_data != "really awake":
                    interval_end_time = last_date_time

                    if interval_start_time != "" and interval_end_time != "":
                        interval_objects.append(
                            dict(start_time=interval_start_time, end_time=interval_end_time, type=interval_type))

                    interval_start_time = minute_data['dateTime']
                    interval_type = "really awake"

                    night_minute_interval[minute_data['dateTime']] = "really awake"
                    night_minute_interval[last_date_time] = last_data
                really_awake_minutes += 1
                last_data = "really awake"
                last_date_time = minute_data['dateTime']

            end_time = minute_data['dateTime']
        no_of_logs += 1
        efficiency += sleep_data['efficiency']
        if no_of_logs == 1:
            start_time = sleep_data['start_time']

    asleep_percentage = float(asleep_minutes / number_of_minutes)
    awake_percentage = float(awake_minutes / number_of_minutes)
    really_awake_percentage = float(really_awake_minutes / number_of_minutes)
    start_time = start_time.split()[1]

    time_summary = {'asleep': minutes_to_hours_minutes(asleep_minutes),
                    'awake': minutes_to_hours_minutes(awake_minutes),
                    'really_awake': minutes_to_hours_minutes(really_awake_minutes),
                    'start_time': start_time,
                    'end_time': end_time,
                    'asleep_percentage': asleep_percentage,
                    'awake_percentage': awake_percentage,
                    'really_awake_percentage': really_awake_percentage,
                    'out_of_bed_percentage': float(
                        1.0 - asleep_percentage - awake_percentage - really_awake_percentage)}
    if no_of_logs == 0:
        sleep_summary = {'message': 'no_records'}
    else:
        sleep_summary = {'efficiency': float(efficiency / no_of_logs), 'date_of_sleep': date_str}

    return dict(interval_objects=interval_objects, time_summary=time_summary, sleep_summary=sleep_summary)


def get_sleep_quality_chart(user_name):
    user = db_session.query(User).filter(User.user_name == user_name).first()

    efficiency_list = []
    for result in perdelta(datetime(2016, 04, 01), datetime.today(), timedelta(days=1)):
        sleeps = db_session.query(Sleep).filter(Sleep.user_id == user.id).filter(
            Sleep.date_of_sleep == str(result.date()))
        date_obj = datetime.strptime(str(result.date()), "%Y-%m-%d")
        no_of_logs = 0
        efficiency = 0
        for sleep in sleeps:
            sleep_data = sleep.get_dict()
            no_of_logs += 1
            efficiency += sleep_data['efficiency']

        if no_of_logs > 0:
            efficiency_list.append({'date': (datetime.combine(date_obj, datetime.min.time()) - epoch).total_seconds(),
                                    'efficiency': float(efficiency / no_of_logs), 'date_human': str(result.date())})
        else:
            efficiency_list.append(
                {'date': (datetime.combine(date_obj, datetime.min.time()) - epoch).total_seconds(), 'efficiency': 0.0,
                 'date_human': str(result.date())})

    return efficiency_list
