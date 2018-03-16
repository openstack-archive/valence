# Copyright (c) 2017 NEC, Corp.
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
from six.moves import http_client

LOG = logging.getLogger(__name__)


OK = http_client.OK
CREATED = http_client.CREATED
NO_CONTENT = http_client.NO_CONTENT


def get(url, http_auth, **kwargs):
    try:
        return requests.request('GET', url, verify=False, auth=http_auth,
                                **kwargs)
    except requests.exceptions.RequestException as ex:
        LOG.error(ex)
        raise ex


def patch(url, http_auth, **kwargs):
    try:
        return requests.request('PATCH', url, verify=False, auth=http_auth,
                                **kwargs)
    except requests.exceptions.RequestException as ex:
        LOG.error(ex)
        raise ex


def post(url, http_auth, data=None, **kwargs):
    try:
        return requests.request('POST', url, data=data, verify=False,
                                auth=http_auth, **kwargs)
    except requests.exceptions.RequestException as ex:
        LOG.error(ex)
        raise ex


def delete(url, http_auth, **kwargs):
    try:
        return requests.request('DELETE', url, verify=False, auth=http_auth,
                                **kwargs)
    except requests.exceptions.RequestException as ex:
        LOG.error(ex)
        raise ex


def put(url, http_auth, **kwargs):
    headers = {"Content-Type": "application/json"}
    try:
        return requests.request('PUT', url, verify=False, headers=headers,
                                auth=http_auth, **kwargs)
    except requests.exceptions.RequestException as ex:
        LOG.error(ex)
        raise ex
