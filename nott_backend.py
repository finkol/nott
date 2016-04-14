import os

from flask import Flask, request, redirect, jsonify

from database import init_db
from services.fitbit_services.fitbit_api import connect_to_fitbit, fetch_access_token
from services.activity import log_activity, get_most_frequent_activity
from services.food import log_food, get_most_frequent_food
from services.sleep import get_sleep_from_fitbit, get_sleep_for_day
import services.user as user_service
from error_handling.generic_error import GenericError
from dateutil import rrule, parser

app = Flask(__name__)
init_db()


@app.route("/")
def hello():
    return "Hello!"


@app.route('/connect_to_fitbit/<user_name>')
def connect_fitbit(user_name=None):
    url = connect_to_fitbit(user_name)
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

    # if 'user_name' in request.args:
    #    user_name = request.args['user_name']

    fetch_access_token(state, code, error)
    return "Hello oauth"


@app.route('/activity', methods=['POST'])
def post_activity():
    if 'user_name' in request.json:
        user_name = request.json.get('user_name')
    else:
        raise GenericError("user_name not provided")

    if 'activity_type' in request.json:
        activity_type = request.json.get('activity_type')
    else:
        raise GenericError("activity_type not provided")

    if 'start_time' in request.json:
        start_time = request.json.get('start_time')
    else:
        raise GenericError("start_time not provided")

    if 'end_time' in request.json:
        end_time = request.json.get('end_time')

    return jsonify(log_activity(user_name, activity_type, start_time, end_time))


@app.route('/food', methods=['POST'])
def post_food():
    if 'user_name' in request.json:
        user_name = request.json.get('user_name')
    else:
        raise GenericError("user_name not provided")

    if 'food_type' in request.json:
        food_type = request.json.get('food_type')
    else:
        raise GenericError("food_type not provided")

    if 'title' in request.json:
        title = request.json.get('title')
    else:
        raise GenericError("title not provided")

    if 'timestamp' in request.json:
        timestamp = request.json.get('timestamp')
    else:
        timestamp = None

    if 'score' in request.json:
        score = request.json.get('score')
    else:
        raise GenericError("score not provided")

    if 'picture' in request.json:
        picture = request.json.get('picture')
    else:
        picture = None

    if 'grams' in request.json:
        grams = request.json.get('grams')
    else:
        grams = 0.0

    return jsonify(log_food(user_name, food_type, title, timestamp, score, picture, grams))


@app.errorhandler(GenericError)
def handle_generic_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/get_sleep')
def get_sleep():
    user_name = request.args['user_name']
    from_date = request.args['from_date']
    to_date = request.args['to_date']
    dates = list(rrule.rrule(rrule.DAILY,
                             dtstart=parser.parse(from_date),
                             until=parser.parse(to_date)))
    return jsonify(sleeps=get_sleep_from_fitbit(user_name, dates))


@app.route('/login', methods=['POST'])
def login():
    if 'user_name' in request.json:
        user_name = request.json.get('user_name')
    else:
        raise GenericError("user_name not provided")

    return jsonify(user_service.login(user_name))


@app.route('/get_frequent_food')
def get_most_frequent_foods():
    user_name = request.args['user_name']
    return jsonify(top3_food=get_most_frequent_food(user_name))


@app.route('/get_frequent_activity')
def get_most_frequent_activities_types():
    user_name = request.args['user_name']
    return jsonify(top3_activity=get_most_frequent_activity(user_name))


@app.route('/get_day_data')
def get_day_data():
    user_name = request.args['user_name']
    date_str = request.args['date_str']
    return jsonify(get_sleep_for_day(user_name, date_str))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 2600))
    app.run(host='0.0.0.0', port=port, debug=True)
