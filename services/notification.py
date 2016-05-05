import json
import requests


def send_notification(alert, list_of_user_ids=[]):
    if list_of_user_ids != None:
        headers = {
            'Accept': 'application/json',
            'Content-type': 'application/json',
        }

        data = {'app_token': '3c5e942f-d1c3-47c0-8c3f-e8e3ecf76c84',
                'app_secret': 'ec781458-9d7e-4eda-b02f-79052d60be75',
                'notification_text': alert,
                'user_ids': list_of_user_ids}

        if len(list_of_user_ids) > 0:
            response = requests.post('https://hideout-noti.herokuapp.com/send', headers=headers,
                                     data=json.dumps(data))
            return response

    return None