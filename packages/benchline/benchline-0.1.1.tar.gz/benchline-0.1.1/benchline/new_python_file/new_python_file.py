# !/usr/bin/python
#
# Author: Paul D. Eden <paul@benchline.org>
# Created: Mon Aug 4, 2008
"""
Script to create new python files quickly.
"""

import os
import sys
import datetime
from string import Template

import six

import benchline.files
import benchline.args
import benchline.command


TEMPLATE_DIR = benchline.files.dir_file_in(__file__)


class NewPythonFile(object):
    """
    This class automates the creation of other new python files
    according to a pre-defined template.

    It also allows for the creation of skeleton test cases
    so that creating unit tests is less time consuming.
    """

    def _make_class_name_from_file_name(self, file_name):
        class_name = os.path.basename(file_name.replace(".py", "").replace("_", " ").title().replace(" ", ""))
        return class_name

    def _get_template_path(self, template_type):
        if template_type == "class":
            template_filename = 'new_class_file.tmpl'
        elif template_type == "cmd":
            template_filename = 'new_cmd_file.tmpl'
        else:
            template_filename = 'new_python_file.tmpl'

        return os.path.join(TEMPLATE_DIR, template_filename)

    def _ask_to_overwrite(self, new_file_name):
        if os.path.exists(new_file_name):
            ans = raw_input("Overwrite %s? " % new_file_name)
            if ans.lower() != "y":
                six.print_("Not overwriting.  %s untouched" % new_file_name)
                sys.exit(0)

    def _write_new_file(self, new_file_name, template):
        class_name = self._make_class_name_from_file_name(new_file_name)
        t = Template(open(self._get_template_path(template), "r").read())
        d = dict(class_name=class_name, date=datetime.date.today().strftime("%Y-%m-%d"))
        fo = open(new_file_name, "w")
        fo.write(t.substitute(d))
        fo.close()

    def make_new_python_file(self, new_file_name, template, noedit, overwrite):
        new_file_name = os.path.realpath(new_file_name)
        if not overwrite:
            self._ask_to_overwrite(new_file_name)
        self._write_new_file(new_file_name, template)
        six.print_("Wrote %s using %s as a template" % (new_file_name, template))
        if not noedit:
            benchline.command.run("vim %s" % new_file_name)


def validate_args(parser, option, args):
    if len(args) < 1:
        parser.error("Please specify the filename of the file to create.")


def main():
    parser = benchline.args.make_parser(__doc__)
    parser.add_option("--template",
                              help="template file to use (one of 'functional'(default), 'class', 'cmd')",
                              default="functional")
    parser.add_option("-n", "--noedit", help="do not edit after create [False]", default=False,
                              action="store_true")
    parser.add_option("-o", "--overwrite", help="overwrite existing files without prompting [False]",
                              default=False,
                              action="store_true")
    options, args = benchline.args.triage(parser, validate_args=validate_args)
    n = NewPythonFile()
    n.make_new_python_file(args[0], options.template,
                           options.noedit, options.overwrite)


if __name__ == "__main__":
    main()
