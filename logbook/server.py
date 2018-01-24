import json


from flask import Flask
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


@app.route('/aircraft')
def aircraft():
    engine = create_engine('sqlite:///logbook.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    return app.response_class(
        response=json.dumps(
            list(session.query(Aircraft).all()),
            cls=AlchemyEncoder,
        ),
        status=200,
        mimetype='application/json',
    )


@app.route('/flights')
def flights():
    engine = create_engine('sqlite:///logbook.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    print([f.pic for f in session.query(Flight).all()])

    return app.response_class(
        response=json.dumps(
            list(session.query(Flight).all()),
            cls=AlchemyEncoder,
        ),
        status=200,
        mimetype='application/json',
    )


def run(port):
    app.run(port=port)
