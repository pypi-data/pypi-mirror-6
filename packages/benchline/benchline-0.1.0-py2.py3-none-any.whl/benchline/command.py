# !/usr/bin/python
#
# Author: Paul D. Eden <paul@benchline.org>
# Created: 2014-03-20
"""
Methods to call os commands more easily.
"""

import subprocess

import benchline.args


def run(cmd, successful_ret_codes=(0,), **kwargs):
    """Wrapper to subprocess.call mimicking subprocess.check_call allowing us to
    specify other successful return codes other than just 0.

    >>> run("ls")
    0

    :param kwargs:
    :param p_open_args:
    :param successful_ret_codes:
    :type successful_ret_codes: list of int
    :return: 0 on success and CalledProcessError Exception on error
    """
    ret_code = subprocess.call(cmd, shell=True, **kwargs)
    if ret_code and ret_code not in successful_ret_codes:
        raise subprocess.CalledProcessError(ret_code, cmd)
    return 0


def output(cmd, successful_ret_codes=(0,), **kwargs):
    """
    Returns the output from cmd as a string

    >>> subprocess.check_output("ls", shell=True) == output("ls")
    True

    :param cmd: an os command to run
    :return: the String output from cmd
    """
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               shell=True, **kwargs)
    output, unused_err = process.communicate()
    ret_code = process.poll()
    if ret_code and ret_code not in successful_ret_codes:
        raise subprocess.CalledProcessError(ret_code, cmd,
                                            output=output)
    return output



if __name__ == "__main__":
    benchline.args.go(__doc__)
