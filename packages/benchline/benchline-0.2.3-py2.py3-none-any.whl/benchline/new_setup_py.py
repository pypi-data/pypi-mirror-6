# !/usr/bin/env python
#
# Author: Paul D. Eden <paul@benchline.org>
# Created: 2014-03-25
"""
Script to create a new setup.py file.
"""
from string import Template
import os

import six

import benchline.args
import benchline.user_input


def validate_args(parser, options, args):
    if len(args) < 1:
        parser.error("The first positional argument must be the project name.")


def get_setup_py(project_str, version_str="0.0.1"):
    template = Template("""# !/usr/bin/env python

from setuptools import setup, find_packages

# we only use the subset of markdown that is also valid reStructuredText so
# that our README.md works on both github (markdown) and pypi (reStructuredText)
with open("README.md") as rm_file:
    long_description = rm_file.read()

setup(name='${project}',
      version='${version}',
      description="TODO",
      long_description=long_description,
      author='TODO',
      author_email='TODO',
      url='TODO',
      packages=find_packages(),
      data_files=[('', ['README.md', 'LICENSE'],)],
      test_suite="${project}.test",
      license="MIT",
      install_requires=['TODO'],
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'TODO = ${project}.todo:main']}
)
""")
    return template.substitute(project=project_str, version=version_str)


def write_setup_py(contents):
    """
    :param contents: setup.py contents
    :return: void
    """
    open("setup.py", "w").write(contents)


def main():
    parser = benchline.args.make_parser(usage="usage: %%prog [options] project_name\n%s" % __doc__)
    parser.add_option("--version", action="store_true",
                      help="version to put in the file. default=0.0.1", default="0.0.1")
    options, args = benchline.args.triage(parser, validate_args=validate_args)
    setup_py_str = get_setup_py(args[0], options.version)
    if os.path.exists("setup.py"):
        yn = benchline.user_input.select("setup.py exists.  overwrite?", ('y', 'n'))
        if yn == 'y':
            write_setup_py(setup_py_str)
        else:
            six.print_("no changes made to setup.py.  existing...")
    else:
        write_setup_py(setup_py_str)


if __name__ == "__main__":
    main()
