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

LOG = logging.getLogger(__name__)


class LogicalDriver(base.ResourceBase):
    identity = base.Field('Id', required=True)
    """The logical driver identity string"""

    name = base.Field('Name')
    """The logical driver name"""

    description = base.Field('Description')
    """The logical driver description"""

    type = base.Field('Type')
    """The logical driver type options values"""

    mode = base.Field('Mode')
    """The logical driver mode options values """

    is_protected = base.Field('Protected')
    """The logical driver protected status (true or false)"""

    image = base.Field('Image')
    """The logical driver image name options values"""

    capacity_gb = base.Field('CapacityGiB')
    """The logical driver capacity GiB"""

    is_bootable = base.Field('Bootable')
    """The logical driver whether it can be booted (true or false)"""

    links = base.Field('Links')
    """The references resource links (dict)"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a Chassis

        :param connector: A Connector instance
        :param identity: The identity of the chassis resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(LogicalDriver, self).__init__(connector,
                                            identity,
                                            redfish_version)

    def refresh(self):
        super(LogicalDriver, self).refresh()

