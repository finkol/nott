import os

from flask import Flask, request, redirect

from database import init_db
from services.fitbit.fitbit_api import connect_to_fitbit, fetch_access_token

app = Flask(__name__)
init_db()


@app.route('/')
def hello_world():
    url = connect_to_fitbit()
    return redirect(url)

@app.route('/oauth')
def fitbit_oauth():
    code = None
    state = None
    error = None
    if 'code' in request.args:
        code = request.args['code']

    if 'state' in request.args:
        state = request.args['state']

    if 'error' in request.args:
        error = request.args['error']

    fetch_access_token(state, code, error)
    return "Hello oauth"


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 2600))
    app.run(host='0.0.0.0', port=port, debug=True)

