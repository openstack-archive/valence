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
from valence.db import api as db_api
from valence.redfish import redfish

LOG = logging.getLogger(__name__)


class Podmanager(object):

    @classmethod
    def _check_creation(cls, values):
        """Checking args when creating a new pod manager

            authentication: should follow the format
            name: can not be duplicated
            url: can not be duplicated

        :values: The properties for this new pod manager.
        :returns: improved values that could be inserted to db
        """

        pod_manager_list = cls.get_podm_list()
        names = [podm['name'] for podm in pod_manager_list]
        urls = [podm['url'] for podm in pod_manager_list]
        if values['name'] in names or values['url'] in urls:
            raise exception.BadRequest('duplicated name or url !')

        # input status
        values['status'] = cls.get_podm_status(values['url'],
                                               values['authentication'])
        return values

    @classmethod
    def _check_updation(cls, values):
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

    @classmethod
    def get_podm_list(cls):
        return map(lambda x: x.as_dict(), db_api.Connection.list_podmanager())

    @classmethod
    def get_podm_by_uuid(cls, uuid):
        return db_api.Connection.get_podmanager_by_uuid(uuid).as_dict()

    @classmethod
    def create_podm(cls, values):
        values = cls._check_creation(values)
        return db_api.Connection.create_podmanager(values).as_dict()

    @classmethod
    def update_podm(cls, uuid, values):
        values = cls._check_updation(values)
        return db_api.Connection.update_podmanager(uuid, values).as_dict()

    @classmethod
    def delete_podm_by_uuid(cls, uuid):
        # TODO(hubian) this need to break the links between podm and its Nodes
        return db_api.Connection.delete_podmanager(uuid)

    @classmethod
    def get_podm_status(cls, url, authentication):
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
