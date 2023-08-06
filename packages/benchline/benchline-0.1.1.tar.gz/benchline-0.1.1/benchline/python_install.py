# !/usr/bin/env python
#
# Author: Paul D. Eden <paul@benchline.org>
# Created: 2014-03-23
"""
Installs the changes to a python project to the local machine.

Just a convenience script.
"""
import benchline.args
import benchline.command


def validate_args(parser, options, args):
    pass


def main():
    options, args = benchline.args.go(__doc__, validate_args=validate_args)
    if options.doctest:
        benchline.command.run("python setup.py test")
        benchline.command.run("python3 setup.py test")
    benchline.command.run("sudo python3 setup.py install")
    benchline.command.run("sudo python setup.py install")


if __name__ == "__main__":
    main()
