import os

from flask import Flask, request

from database import init_db
from services.fitbit.fitbit_api import connect_to_fitbit

app = Flask(__name__)
init_db()


@app.route('/')
def hello_world():
    connect_to_fitbit()
    return 'Hello Nott!'

@app.route('/oauth')
def fitbit_oauth():
    print request.args
    print request.args['code']


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 2600))
    app.run(host='0.0.0.0', port=port, debug=True)

