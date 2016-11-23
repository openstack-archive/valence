# Copyright 2016 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""This Module contains common function used across
   the project

"""


import logging

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


def match_conditions(jsonContent, filterConditions):
    """Generic json filter

       This takes JSON and List of filterconditions
       and returns Boolean. FilterConditions could be
       a path too i.e. Status/State = "Enabled" Returns True
       if the JSON contains Status/State = "Enabled".
       'Values' couldbe case insensitive i.e. Enabled or enabled

    """

    is_conditions_passed = False
    for fc in filterConditions:
        if fc in jsonContent:
            if jsonContent[fc].lower() == filterConditions[fc].lower():
                is_conditions_passed = True
            else:
                is_conditions_passed = False
            break
        elif "/" in fc:
            querylst = fc.split("/")
            tmp = jsonContent
            for q in querylst:
                tmp = tmp[q]
            if tmp.lower() == filterConditions[fc].lower():
                is_conditions_passed = True
            else:
                is_conditions_passed = False
            break
        else:
            LOG.warn(" Filter string mismatch ")
    LOG.Debug(" JSON CONTENT " + str(is_conditions_passed))
    return is_conditions_passed
