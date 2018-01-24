#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path
import re
import sys
from datetime import datetime


from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker


from .models import (
    Aircraft,
    Flight,
)


def parse_args():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='cmd')
    import_parser = subparsers.add_parser(
        'import',
        help='Import a ForeFlight logbook CSV into SQLite',
    )
    import_parser.add_argument(
        'logbook_file',
        type=Path,
        help='Logbook to import',
    )
    import_parser.set_defaults(cmd=cmd_import)

    return parser.parse_args()


def camel_to_snake(string):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def cmd_import(args):
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


def main():
    args = parse_args()
    return args.cmd(args)


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
