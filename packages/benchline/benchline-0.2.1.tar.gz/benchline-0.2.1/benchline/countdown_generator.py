# !/usr/bin/env python
#
# Author: Paul D. Eden <paul@benchline.org>
# Created: 2014-03-24
"""
Script to create the letters for the alphabetic version of countdown,
the game show.
"""
import random
import string
import six

import benchline.args
import benchline.user_input


def validate_args(parser, options, args):
    pass


def random_from_list(lst):
    """Returns a random element in lst

    >>> lst = ['a', 'b', 'c']
    >>> random_from_list(lst) in lst
    True

    :param lst: list of strings
    :return: one random item in the list of strings
    """
    index = random.randint(0, len(lst) - 1)
    return lst[index]


def gen_random_letters(consonant_num, vowel_num):
    """
    Generate a random list of letters with consonant_num consonants and vowel_num vowels

    >>> len(gen_random_letters(1, 3)) == 4
    True

    :param consonant_num:
    :param vowel_num:
    :return: list of letters
    """
    alphabet = [let for let in string.ascii_lowercase]
    vowels = [let for let in "aeiouy"]
    consonants = list(set(alphabet).difference(vowels))
    return_list = []
    for let in range(consonant_num):
        return_list.append(random_from_list(consonants))
    for let in range(vowel_num):
        return_list.append(random_from_list(vowels))
    random.shuffle(return_list)
    return return_list


def main():
    benchline.args.go(__doc__, validate_args=validate_args)
    num_consonants = benchline.user_input.get_int("Enter the number of consonants: ")
    num_vowels = benchline.user_input.get_int("Enter the number of vowels: ")
    six.print_(" ".join(gen_random_letters(num_consonants, num_vowels)))


if __name__ == "__main__":
    main()
