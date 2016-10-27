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
RSA Pod Manager Power Driver using RSA PODM
"""

from ironic.common import states
from ironic.conductor import task_manager
from ironic.drivers import base
from oslo_log import log as logging
from ironic.drivers.modules.rsa_podm import common as rsa_pod_common
from ironic.drivers.modules.rsa_podm import rsa_podm_adapter as pod_manager
from ironic.drivers.modules.rsa_podm import constants

LOG = logging.getLogger(__name__)


class RSAPodmPower(base.PowerInterface):
    """Intel RSA Pod Manager Driver Interface for power-related actions."""

    def get_properties(self):
        return rsa_pod_common.PODM_REQUIRED_PROPERTIES

    def validate(self, task):
        return rsa_pod_common.parse_podm_driver_info(task.node)

    def get_power_state(self, task):
        # only when we need to deploy, we use the context to add node into DB
        pod_manager_obj = pod_manager.get_podm_connection_by_node(None,
                                                                  task.node)
        uuid = task.node.extra['physical_uuid']
        power_state = pod_manager_obj.get_power_state(uuid)
        if power_state == 'unknown':
            return states.ERROR
        else:
            return power_state

    @task_manager.require_exclusive_lock
    def set_power_state(self, task, power_state):
        pod_manager_obj = pod_manager.get_podm_connection_by_node(None,
                                                                  task.node)
        uuid = task.node.extra['physical_uuid']

        if power_state == states.POWER_ON:
            pod_manager_obj.set_power_state(uuid, constants.PODM_POWER_ON_CMD)

        elif power_state == states.POWER_OFF:
            pod_manager_obj.set_power_state(uuid, constants.PODM_POWER_OFF_CMD)

    @task_manager.require_exclusive_lock
    def reboot(self, task):
        pod_manager_obj = pod_manager.get_podm_connection_by_node(None,
                                                                  task.node)
        uuid = task.node.extra['physical_uuid']
        pod_manager_obj.set_power_state(uuid, constants.PODM_POWER_REBOOT_CMD)
