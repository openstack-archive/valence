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

from valence.common import async
from valence.common import exception
from valence.common import utils
import valence.conf
from valence.controller import nodes
from valence.controller import pooled_devices
from valence.db import api as db_api
from valence.podmanagers import manager

CONF = valence.conf.CONF
LOG = logging.getLogger(__name__)


def _check_creation(values):
    """Checking args when creating a new pod manager

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
    # If podmanager 'driver' is None, update as "redfishv1" which is default
    # driver used to manage resources.
    # 'driver' can take values like "redfishv1", "redfishv2" etc.
    values['driver'] = values.get('driver', 'redfishv1')
    return values


def get_podm_list():
    return map(lambda x: x.as_dict(), db_api.Connection.list_podmanager())


def get_podm_by_uuid(uuid):
    return db_api.Connection.get_podmanager_by_uuid(uuid).as_dict()


def create_podmanager(values):
    values = _check_creation(values)
    username, password = utils.get_basic_auth_credentials(
        values['authentication'])
    # Retreive podm connection to get the status of podmanager
    mng = manager.Manager(values['url'], username, password, values['driver'])
    values['status'] = mng.podm.get_status()
    podm = db_api.Connection.create_podmanager(values).as_dict()
    # updates all devices corresponding to this podm in DB
    update_podm_resources_to_db(podm['uuid'])
    return podm


def update_podmanager(uuid, values):
    # Remove uuid and url from values as they can't be updated
    for key in ['uuid', 'url']:
        values.pop(key, None)
    return db_api.Connection.update_podmanager(uuid, values).as_dict()


def delete_podmanager(uuid):
    # For any cleanup driver needs to do (nodes cleanup), before deleting podm
    p_nodes = db_api.Connection.list_composed_nodes({'podm_id': uuid})
    # Delete the nodes w.r.t podmanager from valence DB
    for node in p_nodes:
        nodes.Node(node['uuid']).delete_composed_node()

    # Delete the devices w.r.t podmanager from valence DB
    devices_list = db_api.Connection.list_devices(
        filters={'podm_id': uuid})
    for device in devices_list:
        db_api.Connection.delete_device(device['uuid'])

    return db_api.Connection.delete_podmanager(uuid)


@async.async
def update_podm_resources_to_db(podm_id):
    """Starts asynchronous one_time sync

    As set in configuration this function will sync pooled resources
    one time if background periodic sync is disabled.

    :param podm_id: to asynchronously sync devices of particular podm
    """
    if not CONF.podm.enable_periodic_sync:
        pooled_devices.PooledDevices.synchronize_devices(podm_id)
    return
