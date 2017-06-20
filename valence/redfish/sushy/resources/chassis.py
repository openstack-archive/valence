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


class Chassis(base.ResourceBase):
    asset_tag = base.Field('AssetTag')
    """The chassis asset tag"""

    description = base.Field('Description')
    """The chassis description"""

    identity = base.Field('Id', required=True)
    """The chassis identity string"""

    manufacturer = base.Field('Manufacturer')
    """The chassis manufacturer"""

    name = base.Field('Name')
    """The chassis name"""

    part_number = base.Field('PartNumber')
    """The chassis part number"""

    serial_number = base.Field('SerialNumber')
    """The chassis serial number"""

    sku = base.Field('SKU')
    """The chassis stock-keeping unit"""

    chassis_type = base.Field('ChassisType')
    """The chassis type"""

    oem = base.Field('Oem')
    """The chassis oem options values (dict)"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a Chassis

        :param connector: A Connector instance
        :param identity: The identity of the chassis resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(Chassis, self).__init__(connector, identity, redfish_version)

    def refresh(self):
        super(Chassis, self).refresh()


class ChassisCollection(base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return Chassis

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a ComputerchassisCollection

        :param connector: A Connector instance
        :param path: The canonical path to the chassis collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(ChassisCollection, self).__init__(connector,
                                                path,
                                                redfish_version)
