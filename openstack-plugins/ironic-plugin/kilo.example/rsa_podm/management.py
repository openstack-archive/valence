# Copyright 2015 Lenovo
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Lenovo xClarity Management Driver
"""

from ironic.common import boot_devices
from ironic.conductor import task_manager
from ironic.drivers import base
from ironic.drivers.modules.rsa_podm import common
from oslo_log import log as logging

LOG = logging.getLogger(__name__)

_BOOT_DEVICES_MAP = {
    boot_devices.DISK: 'Hard Disk 0',
    boot_devices.PXE: 'PXE Network',
    boot_devices.CDROM: 'CD/DVD Rom',
}


class RSAManagement(base.ManagementInterface):
    """do the management by RSA Pod Manager Driver"""

    def get_properties(self):
        return common.PODM_REQUIRED_PROPERTIES

    def validate(self, task):
        return common.parse_podm_driver_info(task.node)

    def get_supported_boot_devices(self):
        return list(_BOOT_DEVICES_MAP.keys())

    @task_manager.require_exclusive_lock
    def set_boot_device(self, task, device, persistent=False):
        pass

    def get_boot_device(self, task):
        pass

    def get_sensors_data(self, task):
        raise NotImplementedError()
