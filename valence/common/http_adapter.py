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

import logging

import requests

LOG = logging.getLogger(__name__)


def get_http_request(url, http_auth, **kwargs):
    resp = None
    try:
        resp = requests.request('GET',
                                url,
                                verify=False,
                                auth=http_auth,
                                **kwargs)
    except requests.exceptions.RequestException as e:
        LOG.error(e)
    return resp


def post_http_request(url, http_auth, data=None, **kwargs):
    resp = None
    try:
        resp = requests.request('POST',
                                url,
                                data=data,
                                verify=False,
                                auth=http_auth,
                                **kwargs)
    except requests.exceptions.RequestException as e:
        LOG.error(e)
    return resp
