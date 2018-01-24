#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path
import re
import sys
from datetime import datetime


from sqlalchemy import (
    create_engine,

    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    relationship,
    sessionmaker,
)


Base = declarative_base()


class InitMixin:

    SPECIAL_KEYS = {'class', 'from'}

    def __init__(self, data):
        for k, v in data.items():
            if k in self.SPECIAL_KEYS:
                k = '_' + k
            setattr(self, k, v)


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

    SPECIAL_KEYS = {'class', 'from'}

    def __init__(self, data):
        for k, v in data.items():
            if k in self.SPECIAL_KEYS:
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

    SPECIAL_KEYS = {'class', 'from'}

    def __init__(self, data):
        for k, v in data.items():
            if k in self.SPECIAL_KEYS:
                k = '_' + k
            expect_float = isinstance(
                getattr(self.__class__, k).property.columns[0].type,
                Numeric,
            )
            if expect_float and v == '':
                v = 0.0
            setattr(self, k, v)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'logbook_file',
        type=Path,
        help='Logbook to import',
    )

    return parser.parse_args()


def camel_to_snake(string):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def main():
    args = parse_args()

    aircraft = []
    flights = []

    with args.logbook_file.open(newline='') as f:
        list_to_populate = aircraft
        headers = []
        parse_header_next = False
        for i, row in enumerate(csv.reader(f)):
            if i < 2 or not any(row):
                continue

            if row[0] in {'Aircraft Table', 'Flights Table'}:
                parse_header_next = True
                if 'Aircraft' in row[0]:
                    list_to_populate = aircraft
                else:
                    list_to_populate = flights
                continue

            if parse_header_next:
                for i, entry in enumerate(row):
                    if not entry:
                        break
                headers = []
                for j in range(i):
                    headers.append(camel_to_snake(row[j]))
                parse_header_next = False
                continue

            for i, entry in enumerate(row):
                try:
                    row[i] = datetime.strptime(entry, '%Y-%M-%d').date()
                except ValueError:
                    try:
                        row[i] = json.loads(entry)
                    except json.decoder.JSONDecodeError:
                        pass
            list_to_populate.append(dict(zip(headers, row[:len(headers) + 1])))

    engine = create_engine('sqlite:///logbook.db')

    for cls in [Aircraft, Flight]:
        try:
            cls.__table__.create(engine)
        except OperationalError:
            pass

    Session = sessionmaker(bind=engine)
    session = Session()

    for plane in aircraft:
        session.add(Aircraft(plane))

    for flight in flights:
        session.add(Flight(flight))

    session.commit()
    session.close()

    print('Imported!')

    return True


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
