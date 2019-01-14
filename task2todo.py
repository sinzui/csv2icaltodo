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
UNKNOWN_TEMPLATE = (
    'Unknown headers:\n{}\nThese column headers are understood:\n{}')


def get_csv_tasks(csv_name, verbose=False):
    """Return a list of todo dicts from a CSV file."""
    with open(csv_name, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        csv_todos = list(reader)
    headers = csv_todos[0].keys()
    unknown_headers = set(headers).difference(set(CSV_HEADERS))
    if unknown_headers:
        raise ValueError(UNKNOWN_TEMPLATE.format(unknown_headers, CSV_HEADERS))
    if verbose:
        print('Read {} tasks from {}.'.format(len(csv_todos) - 1, csv_name))
    return csv_todos


def todo_dict_to_ical(todos, calendar_name, verbose=False):
    """Return a dict of calendars and todo lists from a list of todo dicts."""
    calendars = collections.defaultdict(list)
    for todo in todos:
        # Google includes a column named 'list' or 'calendar'
        calendar = todo.pop(ICAL_CALENDAR, calendar_name)
        if TODO_STATUS in todo:
            # Google tasks records status as numbers instead of terms.
            if todo[TODO_STATUS] == '0':
                todo[TODO_STATUS] = 'NEEDS-ACTION'
            elif todo[TODO_STATUS] == '1':
                todo[TODO_STATUS] = 'COMPLETED'
            elif todo[TODO_STATUS] == '2':
                todo[TODO_STATUS] = 'COMPLETED'
                calendar = '{} Archive'.format(calendar)
        parts = ['{}:{}'.format(*i) for i in todo.items()]
        vbody = [TODO_BEGIN] + parts + [TODO_END]
        vtodo = '\n'.join(vbody)
        calendars[calendar].append(vtodo)
    if verbose:
        names = calendars.keys()
        print('Converted and collatted todos into {}.'.format(names))
    return calendars


def put_ical(calendars, calendar_path, verbose=False, dry_run=False):
    """Write dict of calendars and vitem lists to file."""
    for name, vitems in calendars.items():
        parts = [ICAL_BEGIN, ICAL_CALSCALE, ICAL_VERSION] + vitems + [ICAL_END]
        calendar = '\n'.join(parts)
        calendar_name = os.path.join(calendar_path, '{}.ics'.format(name))
        if not dry_run:
            with open(calendar_name, 'w') as cal_file:
                cal_file.write(calendar)
            if verbose:
                print('Wrote vitems to {}'.format(calendar_name))


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
        'csv_name', type=os.path.expanduser,
        help='Path to the sourceCSV file')
    parser.add_argument(
        'calendar_path', type=os.path.expanduser, nargs='?', default='./',
        help='Path to save the ics files to')
    parser.add_argument(
        'calendar_name', nargs='?', default='todos',
        help='Path to the destination ical file')
    args = parser.parse_args(argv)
    return args


def main(argv):
    args = parse_args(argv)
    todos = get_csv_tasks(args.csv_name, args.verbose)
    calendars = todo_dict_to_ical(todos, args.calendar_name, args.verbose)
    put_ical(calendars, args.calendar_path, args.verbose, args.dry_run)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
