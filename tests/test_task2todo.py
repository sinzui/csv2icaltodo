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


def write_file(path, contents):
    with open(path, 'w') as f:
        f.write(contents)


class Csv2IcalTestCase(unittest.TestCase):

    def test_get_args(self):
        args = task2todo.parse_args(['-d', '-v', '~/foo.csv', '~/bar.ical'])
        self.assertTrue(args.dry_run)
        self.assertTrue(args.verbose)
        self.assertEqual('{}/foo.csv'.format(HOME), args.csv_file)
        self.assertEqual('{}/bar.ical'.format(HOME), args.ical_file)
        # Minimal
        args = task2todo.parse_args(['~/foo.csv'])
        self.assertFalse(args.dry_run)
        self.assertFalse(args.verbose)
        self.assertEqual('{}/foo.csv'.format(HOME), args.csv_file)
        self.assertEqual('{}/foo.csv.ical'.format(HOME), args.ical_file)

    def test_get_csv(self):
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
