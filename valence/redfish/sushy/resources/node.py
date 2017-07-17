# Copyright 2017 Red Hat, Inc.
# All Rights Reserved.
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

from sushy.resources import base
from sushy.resources.system import system

LOG = logging.getLogger(__name__)


class Node(base.ResourceBase):
    identity = base.Field('Id', required=True)
    """The node identity string"""

    name = base.Field('Name')
    """The node name"""

    description = base.Field('Description')
    """The node description"""

    oem = base.Field('Oem')
    """The node oem options values (dict)"""

    uuid = base.Field('UUID')
    """The node UUID (same as allocated system)"""

    composed_node_stats = base.Field('ComposedNodeState')
    """The node state of assembly process"""

    links = base.Field('Links')
    """The references resource links (dict)"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a Chassis

        :param connector: A Connector instance
        :param identity: The identity of the chassis resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(Node, self).__init__(connector, identity, redfish_version)

    def refresh(self):
        super(Node, self).refresh()

    def get_system(self):
        system_identity = self.links['ComputerSystem']['@odata.id']
        return system.System(self.connector,
                             system_identity,
                             self.redfish_version)

    def decompose(self):
        pass

    def get_allowed_rest_type(self):
        pass

    def reset(self, action_type):
        pass

    def get_boot_enabled(self):
        pass

    def set_boot_source(self, boot_target):
        pass


class NodeCollection(base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return Node

    def __init__(self, connector, path, redfish_version=None):
        """A Node representing a Node Collection

        :param connector: A Connector instance
        :param path: The canonical path to the chassis collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(NodeCollection, self).__init__(connector,
                                                path,
                                                redfish_version)
