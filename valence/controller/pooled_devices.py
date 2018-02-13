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

from valence.common import exception
from valence.db import api as db_api
from valence.podmanagers import manager

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
    def synchronize_devices(cls, podm_id=None):
        """Sync devices connected to podmanager(s)

        It sync devices corresponding to particular podmanager
        if podm_id is passed. Otherwise, all podmanagers will be
        synced one by one.
        :param podm_id: Optional podm_id to sync respective devices
        :return: Podm_id and status message
        """
        LOG.debug("Synchronizing devices")
        output = []
        response = {}
        if podm_id:
            response['status'] = 'SUCCESS'
            response['podm_id'] = podm_id
            try:
                cls.update_device_info(podm_id)
            except exception.ValenceException:
                LOG.error('Sync of podmanager %s failed' % podm_id)
                response['status'] = 'FAILED'
            output.append(response)
            return output
        podms = db_api.Connection.list_podmanager()
        if not podms:
            return
        for podm in podms:
            response['status'] = 'SUCCESS'
            try:
                response['podm_id'] = podm['uuid']
                cls.update_device_info(podm['uuid'])
            except exception.ValenceException:
                LOG.error('Sync of podmanager %s failed' % podm_id)
                response['status'] = 'FAILED'
            output.append(response)
        return output

    @classmethod
    def update_device_info(cls, podm_id):
        """Update/Add/Delete device info in DB

        It compares all entries in database to data from connected
        resources. Based on computation perform DB operation
        (add/delete/update) on devices.
        :param podm_id: UUID of podmanager
        :return: None
        """
        try:
            LOG.debug('Sync devices managed by podm %s started' % podm_id)
            filters = {'podm_id': podm_id}
            db_device_list = db_api.Connection.list_devices(filters)
            connection = manager.get_connection(podm_id)
            connected_devices = connection.get_all_devices()
            db_processed_devices = []
            for device in connected_devices:
                db_entry = [dev for dev in db_device_list
                            if dev['resource_uri'] == device['resource_uri']]
                # Check if resource entry exist in DB then UPDATE
                if db_entry and \
                   db_entry[0]['pooled_group_id'] != device['pooled_group_id']:
                    values = {'pooled_group_id': device['pooled_group_id'],
                              'node_id': device['node_id'],
                              'state': device['state']
                              }
                    db_api.Connection.update_device(db_entry[0]["uuid"],
                                                    values)
                # Checks if resource doesn't exist in DB then ADD
                elif not db_entry:
                    device['podm_id'] = podm_id
                    db_api.Connection.add_device(device)
                db_processed_devices.append(device['resource_uri'])
            # Checks if resource is no longer existing then DELETE
            db_unprocessed_devices = [
                dev for dev in db_device_list
                if dev['resource_uri'] not in db_processed_devices]
            for device in db_unprocessed_devices:
                db_api.Connection.delete_device(device['uuid'])

        except exception.ValenceException as e:
            LOG.debug("Sync devices failed with exception %s", str(e))
            raise exception.ValenceException("Sync devices failed with "
                                             "exception %s", str(e))
