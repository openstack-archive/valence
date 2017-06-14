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

from valence.common import exception
from valence.conductor.rpcapi import ComputeAPI as compute_api


def _check_creation(values):
    """Checking args when creating a new pod manager

        authentication: should follow the format
        name: can not be duplicated
        url: can not be duplicated

    :values: The properties for this new pod manager.
    :returns: improved values that could be inserted to db
    """

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
    return compute_api.get_podm_list()


def get_podm_by_uuid(uuid):
    return compute_api.get_podm_by_uuid(uuid)


def create_podm(values):
    return compute_api.create_podm(values)


def update_podm(uuid, values):
    return compute_api.update_podm(uuid, values)


def delete_podm_by_uuid(uuid):
    # TODO(hubian) this need to break the links between podm and its Nodes
    return compute_api.delete_podm_by_uuid(uuid)


def get_podm_status(url, authentication):
    """get pod manager running status by its url and auth

    :param url: The url of pod manager.
    :param authentication: array, The auth(s) info of pod manager.

    :returns: status of the pod manager
    """
    return compute_api.get_podm_status(url, authentication)
