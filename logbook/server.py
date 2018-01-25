import json


from flask import (
    send_from_directory,
    Flask,
)
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from .models import (
    Aircraft,
    AlchemyEncoder,
    Flight,
)


app = Flask(__name__, static_url_path='/static')


@app.route('/')
def index():
    return app.send_static_file('html/index.html')


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)


def return_json(text, status):
    return app.response_class(
        response=text,
        status=status,
        mimetype='application/json',
    )


@app.route('/aircraft')
def aircraft():
    engine = create_engine('sqlite:///logbook.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    return return_json(
        json.dumps(
            list(session.query(Aircraft).all()),
            cls=AlchemyEncoder,
        ),
        200,
    )


@app.route('/flights')
def flights():
    engine = create_engine('sqlite:///logbook.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    print([f.pic for f in session.query(Flight).all()])

    return return_json(
        json.dumps(
            list(session.query(Flight).order_by(Flight.date).all()),
            cls=AlchemyEncoder,
        ),
        200,
    )


@app.route('/airport/<path:path>')
def airport(path):
    req = requests.post(
        'https://openflights.org/php/apsearch.php',
        {
            'name': '',
            'iata': '',
            'icao': path.upper(),
            'city': '',
            'country': 'United States',
            'code': 'US',
            'x': '',
            'y': '',
            'elevation': '',
            'timezone': '',
            'dst': 'U',
            'db': 'airports',
            'iatafilter': 'true',
            'apid': '',
            'action': 'SEARCH',
            'offset': '0',
        },
    )
    if req.status_code != 200:
        return return_json(
            json.dumps({'error': 'Unable to process request'}),
            500,
        )

    apt = None
    for airport in req.json()['airports']:
        if airport['icao'] == path.upper():
            apt = airport
            break
    else:
        return return_json(
            json.dumps(
                {'error': 'Unable to find airport {}'.format(path.upper())},
            ),
            404,
        )

    return return_json(json.dumps(apt), 200)


def run(port):
    app.run(port=port)
