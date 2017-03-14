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

from requests import auth

from valence.common import constants
from valence.common import exception
from valence.common import http_adapter
from valence.db import api as db_api
from valence.redfish import redfish

LOG = logging.getLogger(__name__)


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


def _get_basic_auth_from_authentication(authentication):
    """parse out the basic auth from podm's authentication array properties

    :param authentication: podm's authentication

    :return: HTTPBasicAuth of the podm
    """
    for auth_property in authentication:
        if auth_property['type'] == constants.PODM_AUTH_BASIC_TYPE:
            username = auth_property['auth_items']['username']
            password = auth_property['auth_items']['password']
            return auth.HTTPBasicAuth(username, password)
    return None


def get_podm_list():
    return map(lambda x: x.as_dict(), db_api.Connection.list_podmanager())


def get_podm_by_uuid(uuid):
    return db_api.Connection.get_podmanager_by_uuid(uuid).as_dict()


def create_podm(values):
    values = _check_creation(values)
    return db_api.Connection.create_podmanager(values).as_dict()


def update_podm(uuid, values):
    values = _check_updation(values)
    return db_api.Connection.update_podmanager(uuid, values).as_dict()


def delete_podm_by_uuid(uuid):
    # TODO(hubian) this need to break the links between podm and its Nodes
    return db_api.Connection.delete_podmanager(uuid)


def get_podm_status(url, authentication):
    """get pod manager running status by its url and auth

    :param url: The url of pod manager.
    :param authentication: array, The auth(s) info of pod manager.

    :returns: status of the pod manager
    """
    # TODO(Hubian) Only consider and support basic auth type here.
    # After decided to support other auth type this would be improved.
    basic_auth = _get_basic_auth_from_authentication(authentication)

    if basic_auth is None:
        return constants.PODM_STATUS_UNKNOWN

    return redfish.pod_status(url, basic_auth)


def get_podm_usage(podm):
    """get pod manager's systems usage

    :param podm: pod manager dict object of model instance

    :return: the number of systems and nodes
    """
    basic_auth = _get_basic_auth_from_authentication(podm['authentication'])

    systems_url = podm['url'] + '/redfish/v1/Systems'
    systems_resp = http_adapter.get_http_request(systems_url, basic_auth)
    systems_num = systems_resp['Members@odata.count']

    nodes_url = podm['url'] + '/redfish/v1/Nodes'
    nodes_resp = http_adapter.get_http_request(nodes_url, basic_auth)
    nodes_num = nodes_resp['Members@odata.count']

    return {
        "podm_uuid": podm['uuid'],
        "systems": systems_num,
        "nodes": nodes_num,
        "usage": float("%.2f" % (float(nodes_num)/systems_num))
    }


def schedule_podm():
    """schedule out a podm to face the request of composing a new Node

    Choose the podm which systems usage is the minimum value

    :return: the result pod manager
    """
    podm_list = get_podm_list()
    podm_uuid = None
    usage_value = 1
    for podm in podm_list:
        # ignore the un-online pod manager
        if podm['status'] != constants.PODM_STATUS_ONLINE:
            continue
        # find the minimum usage value
        usage = get_podm_usage(podm)
        if usage['usage'] < usage_value:
            podm_uuid = podm['uuid']
            usage_value = usage['usage']

    if podm_uuid is None:
        return None

    return get_podm_by_uuid(podm_uuid)
