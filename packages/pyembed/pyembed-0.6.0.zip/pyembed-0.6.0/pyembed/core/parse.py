# The MIT License(MIT)

# Copyright (c) 2013-2014 Matt Thomson

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from pyembed.core import PyEmbedError
from . import response

from bs4 import BeautifulSoup
import json

RESPONSE_CLASSES = {'photo': response.OEmbedPhotoResponse,
                    'video': response.OEmbedVideoResponse,
                    'link': response.OEmbedLinkResponse,
                    'rich': response.OEmbedRichResponse}


class PyEmbedParseError(PyEmbedError):

    """Thrown if there is an error parsing an OEmbed response."""


def parse_oembed(format, response):
    """Parses an OEmbed response.

    :param format: format of the response.  One of 'json', 'xml'.
    :param response: the OEmbed response, in the given format.
    :returns: an PyEmbedResponse for the given response.
    :raises PyEmbedParseError: if there is an error parsing the response.
    """
    return PARSE_FUNCTIONS[format](response)


def parse_oembed_json(response):
    """Parses a JSON OEmbed response.

    :param response: the OEmbed response, as JSON.
    :returns: an PyEmbedResponse for the given JSON.
    :raises PyEmbedParseError: if there is an error parsing the response.
    """
    value_function = __value_function_json(json.loads(response))
    return __construct_response(value_function)


def parse_oembed_xml(response):
    """Parses an XML OEmbed response.

    :param response: the OEmbed response, as XML.
    :returns: an PyEmbedResponse for the given XML.
    :raises PyEmbedParseError: if there is an error parsing the response.
    """
    soup = BeautifulSoup(response)
    value_function = __value_function_xml(soup.oembed)
    return __construct_response(value_function)


def __value_function_json(value_dict):
    def value_function(field):
        if field in value_dict:
            return value_dict[field]
        else:
            return None

    return value_function


def __value_function_xml(oembed):
    def value_function(field):
        element = oembed.find(field)
        if element:
            try:
                return int(element.text)
            except ValueError:
                return element.text
        else:
            return None

    return value_function


def __construct_response(value_function):
    type = value_function('type')
    if type not in RESPONSE_CLASSES:
        raise PyEmbedParseError('Unknown type: %s', type)

    return RESPONSE_CLASSES[type](value_function)

PARSE_FUNCTIONS = {'json': parse_oembed_json,
                   'xml': parse_oembed_xml}
