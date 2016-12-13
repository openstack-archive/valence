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

from valence.common import constants
from valence.common import exception
from valence.db import api
from valence.redfish import redfish

LOG = logging.getLogger(__name__)

_db_connection = api.Connection()


def _check_creation(values):
    """Checking args when creating a new pod manager

        authentication: should follow the format
        name: can not be duplicated
        url: can not be duplicated

    :values: The properties for this new pod manager.
    :returns: improved values that could be inserted to db
    """

    if not ('name' in values and
            'url' in values and
            'authentication' in values):
        raise exception.BadRequest(detail="Incomplete parameters")
    # check authentication's format and content
    try:
        if not (values['authentication'][0]['type'] and
                values['authentication'][0]['auth_items']):
            LOG.error("invalid authentication when creating podmanager")
            raise exception.BadRequest(detail="invalid "
                                              "authentication properties")
    except KeyError:
        LOG.error("Incomplete parameters when creating podmanager")
        raise exception.BadRequest(detail="invalid "
                                          "authentication properties")

    pod_manager_list = get_podm_list()
    names = [podm['name'] for podm in pod_manager_list]
    urls = [podm['url'] for podm in pod_manager_list]
    if values['name'] in names or values['url'] in urls:
        raise exception.BadRequest('duplicated name or url !')

    # input status
    values['status'] = get_podm_status(values['url'], values['authentication'])

    return values


def _check_updation(values):
    """Checking args when updating a exist pod manager

    :values: The properties of pod manager to be updated
    :returns: improved values that could be updated
    """

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
    values = _check_updation(values)
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
        # TODO(Hubian) Only consider and support basic auth type here.
        # After decided to support other auth type this would be improved.
        if auth['type'] == constants.PODM_AUTH_BASIC_TYPE:
            username = auth['auth_items']['username']
            password = auth['auth_items']['password']
            return redfish.pod_status(url, username, password)

    return constants.PODM_STATUS_UNKNOWN
