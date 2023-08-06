__author__ = 'paul'

import unittest
import doctest

import benchline.args
import benchline.command
import benchline.date_diff
import benchline.files
import benchline.new_python_file.new_python_file
import benchline.python_deploy
import benchline.python_install
import benchline.user_input
import benchline.hours_seconds_2_hours
import benchline.countdown_generator
import benchline.sum_timelog
import benchline.new_setup_py
import benchline.save_line_counts
import benchline.http_format
import benchline.async


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(benchline.args))
    tests.addTests(doctest.DocTestSuite(benchline.command))
    tests.addTests(doctest.DocTestSuite(benchline.date_diff))
    tests.addTests(doctest.DocTestSuite(benchline.files))
    tests.addTests(doctest.DocTestSuite(benchline.new_python_file.new_python_file))
    tests.addTests(doctest.DocTestSuite(benchline.python_deploy))
    tests.addTests(doctest.DocTestSuite(benchline.python_install))
    tests.addTests(doctest.DocTestSuite(benchline.user_input))
    tests.addTests(doctest.DocTestSuite(benchline.hours_seconds_2_hours))
    tests.addTests(doctest.DocTestSuite(benchline.countdown_generator))
    tests.addTests(doctest.DocTestSuite(benchline.sum_timelog))
    tests.addTests(doctest.DocTestSuite(benchline.new_setup_py))
    tests.addTests(doctest.DocTestSuite(benchline.http_format))
    tests.addTests(doctest.DocTestSuite(benchline.async))
    tests.addTests(doctest.DocTestSuite(benchline.save_line_counts))
    return tests


if __name__ == '__main__':
    unittest.main()
