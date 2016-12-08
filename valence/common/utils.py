# Copyright (c) 2016 Intel, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from flask import jsonify
import six


def make_response(json_content="", status_code=200, headers=None):
    """Wrapper function to create flask http response.

    :param json_content: content of http response, should be json object
    :param status_code: status code of http response, set default to 200
    :param headers: additional headers of http response, should be dict
    :returns: return_type -- flask Response object
    """

    response = jsonify(json_content)

    if isinstance(status_code, int):
        response.status_code = status_code
    else:
        raise ValueError("Response status_code should be int object.")

    # Set additional header for http response
    if headers:
        if isinstance(headers, dict):
            for header, value in six.iteritems(headers):
                response.headers[header] = value
        else:
            raise ValueError("Response headers should be dict object.")

    return response
