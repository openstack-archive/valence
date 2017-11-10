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

"""This Module contains common function used across
   the project

"""

import logging

import flask
from oslo_utils import uuidutils

from valence.common import constants

LOG = logging.getLogger(__name__)


def extract_val(data, path, defaultval=None):
    """Generic function to extract value from json

       Function to get value using a key or path
       Example data=json, path = Status/State or Status
       If path not found, then it returns defaultval

    """

    patharr = path.split("/")
    for p in patharr:
        if p in data:
            data = data[p]
        else:
            data = None
            break
    data = (data if data else defaultval)
    return data


def match_conditions(json_content, filter_conditions):
    """Generic json filter

       This takes JSON and List of filter_conditions
       and returns Boolean. FilterConditions could be
       a path too i.e. Status/State = "Enabled" Returns True
       if the JSON contains Status/State = "Enabled".
       'Values' couldbe case insensitive i.e. Enabled or enabled

    """

    is_conditions_passed = False
    for fc in filter_conditions:
        if fc in json_content:
            if json_content[fc].lower() == filter_conditions[fc].lower():
                is_conditions_passed = True
            else:
                is_conditions_passed = False
            break
        elif "/" in fc:
            querylst = fc.split("/")
            tmp = json_content
            for q in querylst:
                tmp = tmp[q]
            if tmp.lower() == filter_conditions[fc].lower():
                is_conditions_passed = True
            else:
                is_conditions_passed = False
            break
        else:
            LOG.warning(" Filter string mismatch ")
    LOG.debug(" JSON CONTENT " + str(is_conditions_passed))
    return is_conditions_passed


def make_response(status_code, content="", headers=None):
    """Wrapper function to create flask http response.

    :param status_code: status code of http response, set default to 200
    :param content: content of http response, should be dict object
    :param headers: additional headers of http response, should be dict
    :returns: return_type -- flask Response object
    """

    response = flask.jsonify(content)

    if isinstance(status_code, int):
        response.status_code = status_code
    else:
        raise ValueError("Response status_code should be int object.")

    # Set additional header for http response
    if headers:
        if isinstance(headers, dict):
            for header, value in headers.items():
                response.headers[header] = value
        else:
            raise ValueError("Response headers should be dict object.")

    return response


def generate_uuid():
    """Generate uniform format uuid"""
    return uuidutils.generate_uuid()


def get_basic_auth_credentials(authentication):
    """parse out the basic auth from podm's authentication array properties

    :param authentication: podm's authentication
    :return: username, password to connect to podmanager
    """
    for auth_property in authentication:
        if auth_property['type'] == constants.PODM_AUTH_BASIC_TYPE:
            username = auth_property['auth_items']['username']
            password = auth_property['auth_items']['password']
            return username, password
