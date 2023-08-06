#!/usr/bin/env python
#
# Author: Paul D. Eden <paul@benchline.org>
# Created: 2014-04-22
"""
Script to format python requests responses as
HTTP text.
"""
import six

import benchline.args


def format_response(headers_dict, body):
    """Formats the response items as an HTTP response
    >>> format_response({"Content-type": "text/plain"}, "this is the response")
    'Content-type: text/plain\\r\\n\\r\\nthis is the response'
    """
    formatted_response = "\r\n".join(["%s: %s" % (key, value) for key, value in six.iteritems(headers_dict)])
    formatted_response += "\r\n\r\n"
    formatted_response += str(body)
    return formatted_response


def format_requests_response(requests_response_obj):
    """Formats a requests module response object
    >>> import requests
    >>> response = requests.get("http://www.byu.edu")
    >>> format_requests_response(response) == format_response(response.headers, response.content)
    True

    :param requests_response_obj: requests module response object
    :return: string
    """
    return format_response(requests_response_obj.headers, requests_response_obj.content)


def main():
    benchline.args.go(__doc__, validate_args=None)


if __name__ == "__main__":
    main()
