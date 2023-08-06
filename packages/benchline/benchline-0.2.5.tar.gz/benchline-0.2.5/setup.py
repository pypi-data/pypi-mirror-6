#!/usr/bin/env python

from setuptools import setup, find_packages

# we only use the subset of markdown that is also valid reStructuredText so
# that our README.md works on both github (markdown) and pypi (reStructuredText)
with open("README.md") as rm_file:
    long_description = rm_file.read()

setup(name='benchline',
      version='0.2.5',
      description="Modules for important things I don't want to reinvent over and over again.",
      long_description=long_description,
      author='Paul D. Eden',
      author_email='paul@benchline.org',
      url='https://github.com/pauldeden/benchline',
      packages=find_packages(),
      data_files=[('', ['README.md', 'LICENSE']),
                  ('benchline/new_python_file', ['benchline/new_python_file/new_python_file.tmpl',
                                                 'benchline/new_python_file/new_class_file.tmpl',
                                                 'benchline/new_python_file/new_cmd_file.tmpl'])],
      test_suite="benchline.test",
      license="MIT",
      install_requires=['requests',
                        'simplejson',
                        'decorator',
                        'ago', 'six', 'peewee'],
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'date_diff = benchline.date_diff:main',
              'python_deploy = benchline.python_deploy:main',
              'python_install = benchline.python_install:main',
              'hours_seconds_2_hours = benchline.hours_seconds_2_hours:main',
              'countdown_generator = benchline.countdown_generator:main',
              'sum_timelog = benchline.sum_timelog:main',
              'new_setup_py = benchline.new_setup_py:main',
              'save_line_counts = benchline.save_line_counts:main',
              'new_python_file = benchline.new_python_file.new_python_file:main']}
)
