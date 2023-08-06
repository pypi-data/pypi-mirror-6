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


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(benchline.args))
    tests.addTests(doctest.DocTestSuite(benchline.command))
    tests.addTests(doctest.DocTestSuite(benchline.date_diff))
    tests.addTests(doctest.DocTestSuite(benchline.files))
    tests.addTests(doctest.DocTestSuite(benchline.new_python_file.new_python_file))
    tests.addTests(doctest.DocTestSuite(benchline.python_deploy))
    tests.addTests(doctest.DocTestSuite(benchline.python_install))
    tests.addTests(doctest.DocTestSuite(benchline.user_input))
    return tests


if __name__ == '__main__':
    unittest.main()
