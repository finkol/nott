import base64

import requests

import services.fitbit_services
from services.fitbit_services.connect_to_fitbit_api import OAuth2Server
from oauthlib.oauth2.rfc6749.errors import MismatchingStateError, MissingTokenError

from database import db_session
from models.user import User


# You'll have to gather the tokens on your own, or use
# ./gather_keys_oauth2.py
#authd_client = fitbit_services.Fitbit('227PT7', '52d59408469ac8aa82d4bdcca69071a6',
                             #access_token='<access_token>', refresh_token='<refresh_token>')
#authd_client.sleep()


def connect_to_fitbit(user_name):
    server = OAuth2Server(client_id='227PT7', client_secret='52d59408469ac8aa82d4bdcca69071a6',
                          redirect_uri="https://nott.herokuapp.com/oauth")
    url = server.browser_authorize(user_name=user_name)

    print('FULL RESULTS = %s' % server.oauth.token)
    print('ACCESS_TOKEN = %s' % server.oauth.token['access_token'])
    print('REFRESH_TOKEN = %s' % server.oauth.token['refresh_token'])
    return url


def fetch_access_token(state, code=None, error=None):
    user = db_session.query(User).filter(User.user_name == state).first()
    server = OAuth2Server(client_id='227PT7', client_secret='52d59408469ac8aa82d4bdcca69071a6',
                          redirect_uri="https://nott.herokuapp.com/oauth")
    if code:
        try:
            access_token = server.oauth.fetch_access_token(code, server.redirect_uri)
            user.fitbit_access_token = str(access_token)
            user.fitbit_user_id = str(access_token['user_id'])
            user.fitbit_state = state
            db_session.flush()
        except MissingTokenError:
            print "Missing access token parameter."
        except MismatchingStateError:
            print "CSRF Warning! Mismatching state"
    else:
        print "Unknown error while authenticating"
    return "Done"


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