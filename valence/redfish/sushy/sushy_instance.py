#!/usr/bin/env python
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

import sushy
from sushy import exceptions

from valence.redfish.sushy.resources import chassis


class RedfishInstance(sushy.Sushy):

    def __init__(self, base_url, username, password):
        """A class representing a Sushy Object Instance

        :param base_url: The base URL to the Redfish controller. It
            should include scheme and authority portion of the URL.
            For example: https://valence.podm:443/
        :param username: User account with admin/server-profile access
            privilege
        :param password: User account password
        """
        super(RedfishInstance, self).__init__(base_url=base_url,
                                              username=username,
                                              password=password)

    def _get_chassis_collection_path(self):
        """Helper function to find the Chassis Collection path"""
        chassis_col = self.json.get('Chassis')
        if not chassis_col:
            raise exceptions.MissingAttributeError(attribute='Chassis',
                                                   resource=self._path)
        return chassis_col.get('@odata.id')

    def get_chassis_collection(self):
        """Get the Chassis Collection object

        :returns: a Chassis Collection object
        """
        return chassis.ChassisCollection(self._conn,
                                         self._get_chassis_collection_path(),
                                         redfish_version=self.redfish_version)

    def get_chassis(self, identity):
        """Given the identity return a Chassis object

        :param identity: The identity of the Chassis resource
        :returns: The Chassis object
        """
        return chassis.Chassis(self._conn,
                               identity,
                               redfish_version=self.redfish_version)
