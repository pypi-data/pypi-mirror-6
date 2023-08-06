#!/usr/bin/python
#
# Author: Paul D. Eden <paul@benchline.org>
# Created: 2014-03-19
"""
Calculates the difference between two dates in days, months and years
and prints them.
"""
import datetime

import ago
import six

import benchline.args


def _valid_date_str(date_str):
    """
    >>> _valid_date_str("2014-02-02")
    True
    >>> _valid_date_str("watermelon")
    False

    :param date_str:
    :return: boolean
    """
    return len(date_str) == 10 and "-" in date_str


def validate_args(parser, options, args):
    if len(args) < 1:
        parser.error("The positional arguments must one or two date strings.")
    if not reduce(lambda x, y: x and y, map(_valid_date_str, args)):
        parser.error("All date args must be in \"YYYY-MM-DD\" format.")


def _parse_date_str(date_str):
    """
    >>> _parse_date_str("2011-01-02")
    datetime.date(2011, 1, 2)
    >>> _parse_date_str("Monday Jan 4th, 2011")
    Traceback (most recent call last):
    ...
    ValueError: time data 'Monday Jan 4th, 2011' does not match format '%Y-%m-%d'
    """
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()


def get_date_from_string(date_str):
    """Returns a date object given a date_str.

    >>> get_date_from_string("2014-02-02")
    datetime.date(2014, 2, 2)
    >>> get_date_from_string("") == datetime.date.today()
    True

    :param date_str:
    :return:
    """
    if date_str:
        return _parse_date_str(date_str)
    else:
        return datetime.date.today()


def main():
    options, args = benchline.args.go(__doc__, usage="usage: %%prog [options] YYYY-MM-DD [YYYY-MM-DD]\n%s" % __doc__,
                               validate_args=validate_args)
    date1 = get_date_from_string(benchline.args.get_arg(args, 0))
    date2 = get_date_from_string(benchline.args.get_arg(args, 1))
    six.print_(ago.human(date1 - date2))


if __name__ == "__main__":
    main()
