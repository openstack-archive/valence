# Copyright (c) 2017 Intel, Inc.
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
from valence.common import utils
from valence.db import api as db_api
from valence.redfish import redfish

LOG = logging.getLogger(__name__)


class Storage(object):

    @classmethod
    def get_storage_resource_by_uuid(cls, drive_uuid):
        """Get storage resource details.

        param drive_uuid: uuid of storage resource
        return: details on the requested resource
        """

        storage_db = db_api.Connection.get_podm_resource_by_uuid(
            drive_uuid).as_dict()
        if storage_db['resource_type'] == "remote_drive":
            storage_hw = redfish.get_remote_drive(storage_db["resource_url"])
        elif storage_db['resource_type'] == "nvme_drive":
            # TODO(ntpttr): When NVMe is added we will check for its type here,
            # and get it through its own redfish call before returning it.
            return
        else:
            raise exception.BadResourceType(
                detail="Requested resource not a type of storage")

        # Add those fields of composed node from db
        storage_hw.update(storage_db)

        return storage_hw

    @classmethod
    def manage_storage(cls, request_body):
        """Add existing RSD storage to Valence DB.

        param request_body: Parameters for storage to manage.

        Required JSON body:

        {
          'resource_url': <Redfish URL of storage to manage>
        }

        return: Info on managed storage.
        """

        storage_resource = redfish.get_drive_by_id(
            request_body['resource_url'])
        # Check to see that the drive to manage doesn't already exist in
        # the Valence database.
        current_storage = cls.list_storage_resources()
        for drive in current_storage:
            if drive['resource_url'] == storage_resource['resource_url']:
                raise exception.ResourceExists(
                    detail="Drive already managed by Valence.")

        storage_resource['uuid'] = utils.generate_uuid()

        # TODO(ntpttr): Add correct podm UUID here when multi-podm is done and
        # this info is used when managing resources. This value is just a shim.
        storage_db = {'uuid': storage_resource['uuid'],
                      'podm_uuid': "UPDATE ME",
                      'resource_url': storage_resource['resource_url'],
                      'resource_type': storage_resource['resource_type']}

        db_api.Connection.create_podm_resource(storage_db)

        return storage_db

    @classmethod
    def list_storage_resources(cls):
        """List all storage resources.

        return: brief info for all storage resources.
        """
        remote_drives = cls.list_remote_drives()
        nvme_drives = cls.list_nvme_drives()
        return remote_drives.update(nvme_drives)

    @classmethod
    def list_remote_drives(cls):
        """List all remote drives.

        return: brief info for all remote drives.
        """
        return [drive_info.as_dict() for drive_info in
                db_api.Connection.list_podm_resources(
                resource_type="remote_drive")]

    @classmethod
    def list_nvme_drives(cls):
        """List all nvme drives.

        return: brief info for all nvme drives.
        """
        return [drive_info.as_dict() for drive_info in
                db_api.Connection.list_podm_resources(
                resource_type="nvme_drive")]

    @classmethod
    def delete_storage_resource(cls, drive_uuid):
        """Delete a storage resource from the database.

        param drive_uuid: uuid of storage drive
        """

        db_api.Connection.delete_podm_resource(drive_uuid)
