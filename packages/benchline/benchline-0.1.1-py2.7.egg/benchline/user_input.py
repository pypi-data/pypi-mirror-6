# !/usr/bin/env python
#
# Author: Paul D. Eden <paul@benchline.org>
# Created: 2014-03-23
"""
Functions for getting user input.
"""
import six

import benchline.args


def validate_args(parser, options, args):
    pass


def select(prompt, valid_values):
    """
    Ask the user to select one of valid_values

    :param prompt: string presented to the user
    :param valid_values: list of strings
    :return: one of the string in valid_values
    """
    response = six.moves.input("%s [%s]: " % (prompt, ", ".join(valid_values)))
    if response in valid_values:
        return response
    else:
        return select(prompt, valid_values)


def get_int(prompt):
    """Prompts the user for an int until they give one.
    :param prompt: string
    :return: the entered int
    """
    ans = six.moves.input(prompt)
    try:
        return int(ans)
    except ValueError:
        return get_int(prompt)


def main():
    benchline.args.go(__doc__, validate_args=validate_args)


if __name__ == "__main__":
    main()
