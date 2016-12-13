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

import requests

from valence.common import constance
from valence.common.exception import BadRequest
from valence.common.exception import NotFound
from valence.db.api import get_connection

_db_connection = get_connection()


def _check_creation(values):
    """Checking args when creating a new pod manager

        name: can not be duplicated
        url: can not be duplicated

    :values: The properties for this new pod manager.
    :returns: improved values that could be inserted to db
    """

    pod_manager_list = get_podm_list()
    names = map(lambda x: x['name'], pod_manager_list)
    urls = map(lambda x: x['url'], pod_manager_list)
    if values['name'] in names or values['url'] in urls:
        raise BadRequest

    # input status
    values['status'] = get_podm_status(values['url'], values['authentication'])

    return values


def _check_updation(uuid, values):
    """Checking args when updating a exist pod manager

    :values: The properties of pod manager to be updated
    :returns: improved values that could be updated
    """

    pod_manager = get_podm_by_uuid(uuid)
    if pod_manager is None:
        raise NotFound

    # uuid, url can not be modified
    if 'uuid' in values:
        values.pop('uuid')
    if 'url' in values:
        values.pop('url')
    return values


def get_podm_list():
    return map(lambda x: x.as_dict(), _db_connection.list_podmanager())


def get_podm_by_uuid(uuid):
    return _db_connection.get_podmanager_by_uuid(uuid).as_dict()


def create_podm(values):
    values = _check_creation(values)
    return _db_connection.create_podmanager(values).as_dict()


def update_podm(uuid, values):
    values = _check_updation(uuid, values)
    return _db_connection.update_podmanager(uuid, values).as_dict()


def delete_podm_by_uuid(uuid):
    # TODO(hubian) this need to break the links between podm and its Nodes
    return _db_connection.delete_podmanager(uuid)


def get_podm_status(url, authentication):
    """get pod manager running status by its url and auth

    :param url: The url of pod manager.
    :param authentication: array, The auth(s) info of pod manager.

    :returns: status of the pod manager
    """
    for auth in authentication:
        try:
            # TODO(Hubian) Only consider and support basic auth type here.
            # After decided to support other auth type this would be improved.
            if auth['type'] == constance.PODM_AUTH_BASIC_TYPE:
                username = auth['auth_items']['username']
                password = auth['auth_items']['password']
                requests.get(url, auth=(username, password))
                return constance.PODM_STATUS_ONLINE
        except requests.ConnectionError:
            return constance.PODM_STATUS_OFFLINE
    return constance.PODM_STATUS_UNKNOWN
