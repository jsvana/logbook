from datetime import date
from decimal import Decimal
import json


from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.ext.declarative import (
    declarative_base,
    DeclarativeMeta,
)
from sqlalchemy.orm import relationship
from sqlalchemy.orm.attributes import InstrumentedAttribute


Base = declarative_base()


class Aircraft(Base):

    __tablename__ = 'aircraft'

    aircraft_id = Column('aircraft_id', String(16), primary_key=True)
    type_code = Column('type_code', String(8))
    year = Column('year', Integer)
    make = Column('make', String(64))
    model = Column('model', String(64))
    category = Column('category', String(64))
    _class = Column('class', String(64))
    gear_type = Column('gear_type', String(64))
    engine_type = Column('engine_type', String(16))
    complex = Column('complex', Boolean)
    high_performance = Column('high_performance', Boolean)
    pressurized = Column('pressurized', Boolean)

    def __init__(self, data):
        for k, v in data.items():
            if k in {'class', 'from'}:
                k = '_' + k
            setattr(self, k, v)


class Flight(Base):

    __tablename__ = 'flights'

    id = Column(Integer, primary_key=True)
    date = Column('date', Date)
    aircraft_id = Column(
        'aircraft_id',
        String(16),
        ForeignKey('aircraft.aircraft_id'),
    )
    _from = Column('from', String(4))
    to = Column('to', String(4))
    route = Column('route', String(512))
    time_out = Column('time_out', String(8))
    time_in = Column('time_in', String(8))
    on_duty = Column('on_duty', String(8))
    off_duty = Column('off_duty', String(8))
    total_time = Column('total_time', Numeric)
    pic = Column('pic', Numeric)
    sic = Column('sic', Numeric)
    night = Column('night', Numeric)
    solo = Column('solo', Numeric)
    cross_country = Column('cross_country', Numeric)
    distance = Column('distance', Numeric)
    day_takeoffs = Column('day_takeoffs', Integer)
    day_landings_full_stop = Column('day_landings_full_stop', Integer)
    night_takeoffs = Column('night_takeoffs', Integer)
    night_landings_full_stop = Column('night_landings_full_stop', Integer)
    all_landings = Column('all_landings', Integer)
    actual_instrument = Column('actual_instrument', Numeric)
    simulated_instrument = Column('simulated_instrument', Numeric)
    hobbs_start = Column('hobbs_start', Numeric)
    hobbs_end = Column('hobbs_end', Numeric)
    tach_start = Column('tach_start', Numeric)
    tach_end = Column('tach_end', Numeric)
    holds = Column('holds', Integer)
    approach1 = Column('approach1', String(64))
    approach2 = Column('approach2', String(64))
    approach3 = Column('approach3', String(64))
    approach4 = Column('approach4', String(64))
    approach5 = Column('approach5', String(64))
    approach6 = Column('approach6', String(64))
    dual_given = Column('dual_given', Numeric)
    dual_received = Column('dual_received', Numeric)
    simulated_flight = Column('simulated_flight', Numeric)
    ground_training = Column('ground_training', Numeric)
    instructor_name = Column('instructor_name', String(64))
    instructor_comments = Column('instructor_comments', String(512))
    person1 = Column('person1', String(64))
    person2 = Column('person2', String(64))
    person3 = Column('person3', String(64))
    person4 = Column('person4', String(64))
    person5 = Column('person5', String(64))
    person6 = Column('person6', String(64))
    flight_review = Column('flight_review', Boolean)
    checkride = Column('checkride', Boolean)
    ipc = Column('ipc', Boolean)

    aircraft = relationship('Aircraft')

    def __init__(self, data):
        for k, v in data.items():
            if k in {'class', 'from'}:
                k = '_' + k
            expect_float = isinstance(
                getattr(self.__class__, k).property.columns[0].type,
                Numeric,
            )
            if expect_float and v == '':
                v = 0.0
            setattr(self, k, v)


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj.__class__, DeclarativeMeta):
            return json.JSONEncoder.default(self, obj)

        fields = {}
        field_names = [
            f for f in dir(obj) if not f.startswith('__')
            and f != 'metadata'
        ]
        for field in field_names:
            try:
                field_val = getattr(obj.__class__, field)
            except Exception:
                continue
            if not isinstance(field_val, InstrumentedAttribute):
                continue
            value = getattr(obj, field)
            if isinstance(value, Decimal):
                value = float(value)
            elif isinstance(value, date):
                value = value.strftime('%Y-%M-%d')
            try:
                json.dumps(value)
                fields[field] = value
            except TypeError:
                fields[field] = None
        return fields
