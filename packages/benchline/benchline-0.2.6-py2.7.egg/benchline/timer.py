# !/usr/bin/env python
#
# Author: Paul D. Eden <paul@benchline.org>
# Created: 2014-04-25
"""
Script to time the execution of python code.
"""
import sys
import time

import benchline.args

if sys.platform == 'win32':
    # On Windows, the best timer is time.clock
    timer_to_use = time.clock
else:
    # On most other platforms the best timer is time.time
    timer_to_use = time.time


def start():
    return timer_to_use()


def stop(start_time):
    return timer_to_use() - start_time


def format_elapsed_time(elapsed_time):
    return "%s seconds" % elapsed_time


def main():
    benchline.args.go(__doc__)


if __name__ == "__main__":
    main()
