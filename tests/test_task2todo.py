from contextlib import contextmanager
import csv
import os
import shutil
import tempfile
import unittest

import task2todo


HOME = os.path.expanduser('~')


@contextmanager
def temp_dir():
    dirname = tempfile.mkdtemp()
    try:
        yield dirname
    finally:
        shutil.rmtree(dirname)


class Csv2IcalTestCase(unittest.TestCase):

    def test_get_args(self):
        args = task2todo.parse_args(
            ['-d', '-v', '~/foo.csv', '~/bar', 'tasks'])
        self.assertTrue(args.dry_run)
        self.assertTrue(args.verbose)
        self.assertEqual('{}/foo.csv'.format(HOME), args.csv_name)
        self.assertEqual('{}/bar'.format(HOME), args.calendar_path)
        self.assertEqual('tasks', args.calendar_name)
        # Minimal
        args = task2todo.parse_args(['~/foo.csv'])
        self.assertFalse(args.dry_run)
        self.assertFalse(args.verbose)
        self.assertEqual('{}/foo.csv'.format(HOME), args.csv_name)
        self.assertEqual('./', args.calendar_path)
        self.assertEqual('todos', args.calendar_name)

    def test_get_csv_tasks(self):
        with temp_dir() as path:
            # Bad format.
            csv_name = os.path.join(path, 'test.csv')
            with open(csv_name, 'w') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(['name', 'start', 'end', 'place', 'notes'])
                writer.writerow([
                    'first', '2019-01-12', '2019-01-13', 'blue', 'meeting'])
            self.assertRaises(ValueError, task2todo.get_csv_tasks, csv_name)
            # Good format
            with open(csv_name, 'w') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(task2todo.CSV_HEADERS)
                writer.writerow([
                    'first', '2019-01-12 13:00;00', '2019-01-12 14:00;00',
                    'blue room', 'test meeting'])
            csv_data = task2todo.get_csv_tasks(csv_name)
            self.assertEqual(1, len(csv_data))
            self.assertEqual('first', csv_data[0][task2todo.TODO_SUMMARY])

    @staticmethod
    def make_csv_todo(summary, status='NEEDS-ACTION', calendar=None):
        todo = {
            task2todo.TODO_SUMMARY: summary,
            task2todo.TODO_STATUS: status,
            task2todo.TODO_DTSTAMP: '20181222T174737Z',
            }
        if calendar:
            todo[task2todo.ICAL_CALENDAR] = calendar
        return todo

    def test_todo_dict_to_ical(self):
        todos = [
            self.make_csv_todo('one', status='NEEDS-ACTION', calendar='foo'),
            self.make_csv_todo('two', status='COMPLETED'),
            self.make_csv_todo('three', status='0'),
            self.make_csv_todo('four', status='1'),
            self.make_csv_todo('five', status='2'),
            ]
        calendars = task2todo.todo_dict_to_ical(todos, 'todos')
        self.assertEqual(2, len(calendars))
        self.assertEqual(1, len(calendars['foo']))
        vtodo = calendars['foo'][0]
        self.assertEqual(
            'BEGIN:VTODO\nSTATUS:NEEDS-ACTION\nDTSTAMP:20181222T174737Z'
            '\nSUMMARY:one\nEND:VTODO',
            vtodo)
        vtodo = calendars['todos'][0]
        self.assertIn('\nSUMMARY:two\n', vtodo)
        self.assertIn('\nSTATUS:COMPLETED\n', vtodo)
        vtodo = calendars['todos'][1]
        self.assertIn('\nSUMMARY:three\n', vtodo)
        self.assertIn('\nSTATUS:NEEDS-ACTION\n', vtodo)
        vtodo = calendars['todos'][2]
        self.assertIn('\nSUMMARY:four\n', vtodo)
        self.assertIn('\nSTATUS:COMPLETED\n', vtodo)
        vtodo = calendars['todos'][3]
        self.assertIn('\nSUMMARY:five\n', vtodo)
        self.assertIn('\nSTATUS:COMPLETED\n', vtodo)

    def test_put_ical(self):
        todos = [
            self.make_csv_todo('one', status='NEEDS-ACTION', calendar='foo'),
            self.make_csv_todo('two', status='COMPLETED'),
            self.make_csv_todo('three', status='COMPLETED'),
            ]
        calendars = task2todo.todo_dict_to_ical(todos, 'todos')
        with temp_dir() as calendar_path:
            task2todo.put_ical(calendars, calendar_path)
            file_names = os.listdir(calendar_path)
            self.assertIn('todos.ics', file_names)
            self.assertIn('foo.ics', file_names)
            with open(os.path.join(calendar_path, 'foo.ics')) as ics_file:
                data = ics_file.read()
            self.assertEqual(
                'BEGIN:VCALENDAR\nCALSCALE:GREGORIAN\nVERSION:2.0'
                '\nBEGIN:VTODO\nSTATUS:NEEDS-ACTION\nDTSTAMP:20181222T174737Z'
                '\nSUMMARY:one\nEND:VTODO'
                '\nEND:VCALENDAR',
                data)
            with open(os.path.join(calendar_path, 'todos.ics')) as ics_file:
                data = ics_file.read()
            self.assertIn('\n{}\n'.format(calendars['todos'][0]), data)
            self.assertIn('\n{}\n'.format(calendars['todos'][1]), data)
