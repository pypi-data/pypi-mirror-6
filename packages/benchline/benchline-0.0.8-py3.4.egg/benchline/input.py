# !/usr/bin/env python
#
# Author: Paul D. Eden <paul@benchline.org>
# Created: 2014-03-23
"""
Functions for getting user input.
"""
import benchline.args

# setup input function to work in both python 2 and 3
try:
    input = raw_input
except NameError:
    pass


def validate_args(parser, options, args):
    pass


def select(prompt, valid_values):
    """
    Ask the user to select one of valid_values

    :param prompt: string presented to the user
    :param valid_values: list of strings
    :return: one of the string in valid_values
    """
    response = input(prompt)
    if response in valid_values:
        return response
    else:
        return select(prompt, valid_values)


def main():
    benchline.args.go(__doc__, validate_args=validate_args)


if __name__ == "__main__":
    main()
