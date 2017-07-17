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

from six.moves import http_client
from sushy.resources import base
from sushy.resources.system import system
from sushy.resources.system import constants as sys_cons

from valence.common import exception


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
        self.system = system.System(self.connector,
                                    self.links['ComputerSystem']['@odata.id'],
                                    self.redfish_version)

    def refresh(self):
        super(Node, self).refresh()

    def get_system(self):
        return self.system

    def get_storage(self):
        pass

    def decompose(self):
        resp = self._conn._op(method='DELETE', path=self.identity)
        if resp.status_code == http_client.NO_CONTENT:
            # we should return 200 status code instead of 204
            # because 204 means 'No Content', the message in resp_dict will
            # be ignored in that way
            return exception.confirmation(
                confirm_code="DELETED",
                confirm_detail="This node has been deleted successfully."
            )
        else:
            raise exception.RedfishException(resp.json(),
                                             status_code=resp.status_code)

    def get_allowed_rest_type(self):
        """Get the allowed values for resetting the node.

        Actually this would comes from the node's allocated system's values

        :returns: A set with the allowed values.
        """
        return self.system.get_allowed_reset_system_values()

    def reset(self, value):
        """Reset the node.

        :param value: The target value.
        :raises: InvalidParameterValueError, if the target value is not
            allowed.
        """
        self.system.reset_system(value)

    def get_allowed_node_boot_source_values(self):
        """Get the allowed values for changing the boot source.

        :returns: A set with the allowed values.
        """
        return self.system.get_allowed_system_boot_source_values()

    def set_boot_source(self, target,
                        enabled=sys_cons.BOOT_SOURCE_ENABLED_ONCE,
                        mode=None):
        """Set the boot source.

        Set the boot source to use on next reboot of the System.

        :param target: The target boot source.
        :param enabled: The frequency, whether to set it for the next
            reboot only (BOOT_SOURCE_ENABLED_ONCE) or persistent to all
            future reboots (BOOT_SOURCE_ENABLED_CONTINUOUS) or disabled
            (BOOT_SOURCE_ENABLED_DISABLED).
        :param mode: The boot mode, UEFI (BOOT_SOURCE_MODE_UEFI) or
            BIOS (BOOT_SOURCE_MODE_BIOS).
        :raises: InvalidParameterValueError, if any information passed is
            invalid.
        """
        self.system.set_system_boot_source(target, enabled, mode)


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

    def compose_new_node(self, compose_request_body):
        """compose a new node

        :param compose_request_body: compose request body kwargs
        :return: node object info
        """
        compose_url = self._path + '/Actions/Allocate'
        allocate_resp = self._conn.post(compose_url,
                                        data=compose_request_body,
                                        headers={
                                            'Content-type': 'application/json'
                                        })
        if allocate_resp.status_code != http_client.CREATED:
            # Raise exception if allocation failed
            raise exception.RedfishException(allocate_resp.json(),
                                             status_code=allocate_resp.status_code)

        # Allocated node successfully
        node_url = allocate_resp.headers['Location']
        LOG.debug('Successfully allocated node:' + node_url)

        # Get url of assembling node
        resp = self._conn.get(node_url)
        respdata = resp.json()
        assemble_url = respdata['Actions']['#ComposedNode.Assemble']['target']

        # Assemble node
        LOG.debug('Assembling Node: {0}'.format(assemble_url))
        assemble_resp = self._conn.post(assemble_url)

        # Node Object
        node = Node(self._conn, node_url, self.redfish_version)

        if assemble_resp.status_code != http_client.NO_CONTENT:
            # Delete node if assemble failed
            node.decompose()
            raise exception.RedfishException(assemble_resp.json(),
                                             status_code=resp.status_code)
        else:
            # Assemble successfully
            LOG.debug('Successfully assembled node: ' + node_url)

        # return node object
        return node
