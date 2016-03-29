import services.fitbit
from services.fitbit.connect_to_fitbit_api import OAuth2Server
from oauthlib.oauth2.rfc6749.errors import MismatchingStateError, MissingTokenError


# You'll have to gather the tokens on your own, or use
# ./gather_keys_oauth2.py
#authd_client = fitbit.Fitbit('227PT7', '52d59408469ac8aa82d4bdcca69071a6',
                             #access_token='<access_token>', refresh_token='<refresh_token>')
#authd_client.sleep()


def connect_to_fitbit():
    #authd_client = services.fitbit.FitbitOauth2Client(client_id='227PT7', client_secret='52d59408469ac8aa82d4bdcca69071a6')
    #code = authd_client.authorize_token_url(scope=["sleep"])
    #print code[1]
    #access_token = authd_client.fetch_access_token(code=code[1], redirect_uri="http://0.0.0.0:2600/")
    #print access_token
    #print authd_client.make_request("https://api.fitbit.com/1/user/-/sleep/date/2014-09-01.json", method='GET')

    server = OAuth2Server(client_id='227PT7', client_secret='52d59408469ac8aa82d4bdcca69071a6',
                          redirect_uri="http://0.0.0.0:2600/oauth")
    url = server.browser_authorize()

    print('FULL RESULTS = %s' % server.oauth.token)
    print('ACCESS_TOKEN = %s' % server.oauth.token['access_token'])
    print('REFRESH_TOKEN = %s' % server.oauth.token['refresh_token'])
    return url


def fetch_access_token(state, code=None, error=None):
    server = OAuth2Server(client_id='227PT7', client_secret='52d59408469ac8aa82d4bdcca69071a6',
                          redirect_uri="http://0.0.0.0:2600/oauth")
    if code:
        try:
            server.oauth.fetch_access_token(code, server.redirect_uri)
        except MissingTokenError:
            print "Missing access token parameter."
            #error = self._fmt_failure(
             #   'Missing access token parameter.</br>Please check that '
              #  'you are using the correct client_secret')
        except MismatchingStateError:
            print "CSRF Warning! Mismatching state"
            #error = self._fmt_failure('CSRF Warning! Mismatching state')
    else:
        print "Unknown error while authenticating"
        #error = self._fmt_failure('Unknown error while authenticating')
    # Use a thread to shutdown cherrypy so we can return HTML first
    #self._shutdown_cherrypy()
    #return error if error else self.success_html
    return "Done"

