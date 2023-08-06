# !/usr/bin/python
#
# Author: Paul D. Eden <paul@benchline.org>
# Created: 2014-03-20
"""
Methods to interact with directories.
"""
import os
import random

import benchline.args


def dir_file_in(file_name):
    """Returns the OS directory where file_name resides.
    To return the directory of the current file use __file__ as
    file_name.

    >>> filename = str(random.random())
    >>> cwd = os.getcwd()
    >>> open(filename, "w").close()
    >>> dir_file_in(filename) == cwd
    True
    >>> os.remove(filename)
    """
    return os.path.dirname(os.path.realpath(file_name))


if __name__ == "__main__":
    benchline.args.go(__doc__)
