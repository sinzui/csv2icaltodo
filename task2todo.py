#!/usr/bin/python

from __future__ import print_function

from argparse import ArgumentParser
import collections
import csv
import os
import sys


ICAL_CALENDAR = 'CALENDAR'
ICAL_BEGIN = 'BEGIN:VCALENDAR'
ICAL_CALSCALE = 'CALSCALE:GREGORIAN'
ICAL_VERSION = 'VERSION:2.0'
ICAL_END = 'END:VCALENDAR'
TODO_BEGIN = 'BEGIN:VTODO'
TODO_SUMMARY = 'SUMMARY'
TODO_DTSTAMP = 'DTSTAMP'
TODO_DUE = 'DUE'
TODO_RRULE = 'RRULE'
TODO_PRIORITY = 'PRIORITY'
TODO_STATUS = 'STATUS'
TODO_CREATED = 'CREATED'
TODO_COMPLETED = 'COMPLETED'
TODO_SEQUENCE = 'SEQUENCE'
TODO_LOCATION = 'LOCATION'
TODO_DESCRIPTION = 'DESCRIPTION'
TODO_END = 'END:VTODO'
CSV_HEADERS = [
    TODO_SUMMARY, TODO_DTSTAMP, TODO_DUE, TODO_RRULE, TODO_PRIORITY,
    TODO_STATUS, TODO_CREATED, TODO_COMPLETED, TODO_SEQUENCE, TODO_LOCATION,
    TODO_DESCRIPTION, ICAL_CALENDAR]
DEFAULT_CALENDAR = 'DEFAULT'


def get_csv_tasks(csv_name, verbose=False):
    """Return a list of todo dicts from a CSV file."""
    with open(csv_name, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        csv_todos = list(reader)
    headers = csv_todos[0].keys()
    if set(headers) != set(CSV_HEADERS):
        raise ValueError(
            'The CSV file requires these column headers:\n{}'.format(
                CSV_HEADERS))
    return csv_todos


def todo_dict_to_ical(todos, verbose=False):
    """Return a list of todo calendars converted from a list of todo dicts."""
    calendars = collections.defaultdict(list)
    for todo in todos:
        if TODO_STATUS in todo:
            # Google tasks records status as numbers instead of terms.
            if todo[TODO_STATUS] == '0':
                todo[TODO_STATUS] = 'NEEDS-ACTION'
            elif todo[TODO_STATUS] in ['1', '2']:
                todo[TODO_STATUS] = 'COMPLETED'
        calendar = todo.pop(ICAL_CALENDAR, DEFAULT_CALENDAR)
        vbody = ['{}:{}'.format(*i) for i in todo.items()]
        vbody.insert(0, TODO_BEGIN)
        vbody.append(TODO_END)
        vtodo = '\n'.join(vbody)
        calendars[calendar].append(vtodo)
    return calendars


def put_ical(ical_data, ical_name, verbose=False, dry_run=False):
    """Write ical_data to the file ical_name."""


def parse_args(argv=None):
    """Return the argument parser for this program."""
    parser = ArgumentParser(description='Convert CSV data to ICal format.')
    parser.add_argument(
        '-d', '--dry-run', action='store_true', default=False,
        help='Do not make changes.')
    parser.add_argument(
        '-v', '--verbose', action="store_true", default=False,
        help='Increase verbosity.')
    parser.add_argument(
        'csv_file', type=os.path.expanduser,
        help='Path to the sourceCSV file')
    parser.add_argument(
        'ical_file', type=os.path.expanduser, nargs='?',
        help='Path to the destination ical file')
    args = parser.parse_args(argv)
    if not getattr(args, 'ical_file'):
        args.ical_file = '{}.ical'.format(args.csv_file)
    return args


def main(argv):
    args = parse_args(argv)
    csv_data = get_csv_tasks(args.csv_name,  args.verbose, args.dry_run)
    ical_data = todo_dict_to_ical(csv_data, args.verbose)
    put_ical(ical_data, args.ical_name, args.verbose, args.dry_run)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
