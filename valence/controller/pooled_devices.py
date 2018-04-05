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

from futurist import periodics

from valence.common import exception
import valence.conf
from valence.db import api as db_api
from valence.podmanagers import manager

CONF = valence.conf.CONF
LOG = logging.getLogger(__name__)


class PooledDevices(object):

    @staticmethod
    def _show_device_brief_info(device_info):
        return {key: device_info[key] for key in device_info.keys()
                if key in ['uuid', 'podm_id', 'type', 'state', 'node_id',
                           'resource_uri', 'pooled_group_id']}

    @classmethod
    def list_devices(cls, filters={}):
        """List all registered devices

        :param filters: filter by key, value arguments

        Eg: {'podm_id': 'xxxx', 'type': 'SSD'}

        :return: List of devices
        """
        devices = db_api.Connection.list_devices(filters)
        return [cls._show_device_brief_info(dev.as_dict()) for dev in devices]

    @classmethod
    def get_device(cls, device_id):
        """Get device info

        :param device_id: UUID of device
        :return: DB device info
        """
        return db_api.Connection.get_device_by_uuid(device_id).as_dict()

    @classmethod
    @periodics.periodic(spacing=CONF.podm.sync_interval, enabled=True,
                        run_immediately=True)
    def synchronize_devices(cls, podm_id=None):
        """Sync devices connected to podmanager(s)

        It sync devices corresponding to particular podmanager
        if podm_id is passed. Otherwise, all podmanagers will be
        synced one by one.
        :param podm_id: Optional podm_id to sync respective devices
        :return: Podm_id and status message
        """
        output = []
        if podm_id:
            LOG.debug('Synchronizing devices connected to podm %s', podm_id)
            output.append(cls.update_device_info(podm_id))
            return output
        podms = db_api.Connection.list_podmanager()
        for podm in podms:
            LOG.debug('Synchronizing devices connected to podm %s',
                      podm['uuid'])
            output.append(cls.update_device_info(podm['uuid']))
        return output

    @classmethod
    def update_device_info(cls, podm_id):
        """Update/Add/Delete device info in DB

        It compares all entries in database to data from connected
        resources. Based on computation perform DB operation
        (add/delete/update) on devices.
        :param podm_id: UUID of podmanager
        :return: Dictionary containing update status of podm
        """
        LOG.debug('Update device info managed by podm %s started', podm_id)
        response = dict()
        response['podm_id'] = podm_id
        try:
            db_devices = db_api.Connection.list_devices({'podm_id': podm_id})
            connection = manager.get_connection(podm_id)
            podm_devices = {}
            for device in connection.get_all_devices():
                podm_devices[device['resource_uri']] = device
            for db_dev in db_devices:
                podm_dev = podm_devices.get(db_dev['resource_uri'], None)
                if not podm_dev:
                    # device is disconnected, remove from db
                    db_api.Connection.delete_device(db_dev['uuid'])
                    continue
                if db_dev['pooled_group_id'] != podm_dev['pooled_group_id']:
                    # update device info
                    values = {'pooled_group_id': podm_dev['pooled_group_id'],
                              'node_id': podm_dev['node_id'],
                              'state': podm_dev['state']
                              }
                    db_api.Connection.update_device(db_dev["uuid"], values)
                    del podm_devices[db_dev['resource_uri']]
                    continue
                # remove device i.e already updated
                del podm_devices[db_dev['resource_uri']]
            # Add remaining devices available in podm_devices
            for dev in podm_devices.values():
                dev['podm_id'] = podm_id
                db_api.Connection.add_device(dev)
            response['status'] = 'SUCCESS'

        except exception.ValenceError:
            LOG.exception("Failed to update resources from podm")
            response['status'] = 'FAILED'
        return response
