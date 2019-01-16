# Convert CSV Files to ICal Todos

This script converts task lists exported to CSV format into ICal todo lists.

These headers are supported: SUMMARY, DTSTAMP, DUE, RRULE, PRIORITY,
STATUS, CREATED, COMPLETED, SEQUENCE, LOCATION, DESCRIPTION. You can rename
headers in an existing CSV to match the supported headers, then delete the
unsupported headers and columns.

A non-standard column named CALENDAR is supported so that todos from multiple
lists can be converted. Each list is written as separate file.

## Google tasks

CSV exports of Google tasks can be converted. The leading rows and extra columns
can be deleted after updating the headings to the supported named.

Google task status is converted to ICal NEED-ACTION or COMPLETED. If the status
is archived, the status is set to COMPLETED and moved to a separate file that
you can import if you want history.

## Usage

```bash
usage: task2todo.py [-h] [-d] [-v] csv_name [calendar_path] [calendar_name]

Convert CSV data to ICal format.

positional arguments:
  csv_name       Path to the sourceCSV file
  calendar_path  Path to save the ics files to
  calendar_name  Path to the destination ical file

optional arguments:
  -h, --help     show this help message and exit
  -d, --dry-run  Do not make changes.
  -v, --verbose  Increase verbosity.
```
