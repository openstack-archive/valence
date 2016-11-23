__author__ = 'zhangyufei'

import requests
import json

from ironic.common import boot_devices
from ironic.common import exception
from ironic.common.i18n import _

from ironic.common import states
from ironic.conductor import task_manager
from ironic.drivers import base
from ironic.drivers import utils as driver_utils


REQUIRED_PROPERTIES = {
    'podm_address': _("IP address of the podmanager. Required."),
}

OPTIONAL_PROPERTIES = {
    'min_cpu': _("min num of cpus."),
    'min_ram': _("min num of ram."),
    'remote_storage': _("remote storage allocated."),
    'podm_username': _("username. Required."),
    'podm_password': _("password. Required."),
}

POWER_ON = 'On'
POWER_OFF = 'ForceOff'
REBOOT = 'ForceRestart'

_STR_ZERO = '0'

_baseHeaders={'Content-Type':'application/json'}

COMMON_PROPERTIES = REQUIRED_PROPERTIES.copy()
COMMON_PROPERTIES.update(OPTIONAL_PROPERTIES)

def _parse_driver_info(node):
    info = node.driver_info or {}
    missing_info = [key for key in REQUIRED_PROPERTIES if not info.get(key)]
    if missing_info:
        raise exception.MissingParameterValue(
            _("Missing the following credentials in node's"
              " driver_info: %s.") % missing_info)

    podm_address = info.get('podm_address')
    podm_username = info.get('podm_username')
    podm_password = info.get('podm_password')

    min_cpu = info.get('min_cpu') or _STR_ZERO
    min_ram = info.get('min_ram') or _STR_ZERO
    remote_storage = info.get('remote_storage') or _STR_ZERO

    podm_node_id = info.get('podm_node_id')

    if not podm_node_id:
        node_detail = _compose_node(podm_address = podm_address,
                                     min_cpu = min_cpu,
                                     min_ram = min_ram,
                                     remote_storage = remote_storage)
        if node_detail:
            node.driver_info['podm_node_id']=node_detail.get('Id')

        else:
            raise exception.InvalidParameterValue(_(
            "Invalid RSC config, can't allocated nodes"))

    return {
        'podm_address': podm_address,
        'podm_username': podm_username,
        'podm_password': podm_password,
        'podm_node_id': podm_node_id
    }

def _compose_node(podm_address,min_cpu=_STR_ZERO,
                  min_ram=_STR_ZERO,remote_storage=_STR_ZERO):
    mem_args = '"Memory":[{"CapacityMiB":%s}]' % min_ram
    cpu_args = '"Processors":[{"TotalCores":%s}]' % min_cpu
    disk_args = '"RemoteDrives": [{"CapacityGiB":%s, "iSCSIAddress": "iqn.2016-09.com.openstack:storage.disk"}]' % remote_storage

    url = 'http://%s:8181/v1/nodes/' % podm_address
    if remote_storage != _STR_ZERO:
        data = '{%s,%s}' % (mem_args, disk_args)
    else:
        data = '{%s}' % (mem_args)

    res = requests.post(url, data=data, headers=_baseHeaders)
    if res.ok:
        return json.loads(res.content)
    return None

def _destroy_node(node):
    driver_info = node.driver_info or {}
    podm_node_id = driver_info.get('podm_node_id')
    podm_address = driver_info.get('podm_address')

    url = 'http://%s:8181/v1/nodes/%s' % (podm_address,podm_node_id)
    requests.delete(url,headers=_baseHeaders)

def _set_action(action, driver_info):
    address = driver_info.get('podm_address')
    node_id = driver_info.get('podm_node_id')
    url = 'http://%s:8181/v1/power' % address
    data =  '{"node_id":"%s","power_action":"%s"}' % (node_id, action)
    requests.post(url, data=data, headers=_baseHeaders)

def _power_on(driver_info):
    """Turn the power ON for this node.

    """
    _set_action(POWER_ON, driver_info)


def _power_off(driver_info):
    """Turn the power OFF for this node.

    """
    _set_action(POWER_OFF, driver_info)


def _node_detail(driver_info):
    address = driver_info.get('podm_address')
    node_id = driver_info.get('podm_node_id')
    if not node_id:
        raise exception.InvalidParameterValue(
                _("_power_status called "
                  "without power node-id %s."))

    url = 'http://%s:8181/v1/nodes/%s' % (address, node_id)

    res = requests.get(url, headers=_baseHeaders)
    node = res.content
    return json.loads(node)


def _power_status(driver_info):
    node = _node_detail(driver_info)
    return (states.POWER_ON if node.get('ComposedNodeState') == 'PoweredOn'
            else states.POWER_OFF)

class RSCPower(base.PowerInterface):

    def __init__(self):
        pass

    def get_properties(self):
        return COMMON_PROPERTIES

    def validate(self, task):
        """Validate driver_info for ipmitool driver.

        Check that node['driver_info'] contains IPMI credentials.

        :param task: a TaskManager instance containing the node to act on.
        :raises: InvalidParameterValue if required ipmi parameters are missing.
        :raises: MissingParameterValue if a required parameter is missing.

        """
        _parse_driver_info(task.node)
        # NOTE(deva): don't actually touch the BMC in validate because it is
        #             called too often, and BMCs are too fragile.
        #             This is a temporary measure to mitigate problems while
        #             1314954 and 1314961 are resolved.

    def get_power_state(self, task):
        """Get the current power state of the task's node.

        :param task: a TaskManager instance containing the node to act on.
        :returns: one of ironic.common.states POWER_OFF, POWER_ON or ERROR.
        :raises: InvalidParameterValue if required ipmi parameters are missing.
        :raises: MissingParameterValue if a required parameter is missing.
        :raises: IPMIFailure on an error from ipmitool (from _power_status
            call).

        """
        driver_info = _parse_driver_info(task.node)
        return _power_status(driver_info)

    @task_manager.require_exclusive_lock
    def set_power_state(self, task, pstate):
        """Turn the power on or off.

        :param task: a TaskManager instance containing the node to act on.
        :param pstate: The desired power state, one of ironic.common.states
            POWER_ON, POWER_OFF.
        :raises: InvalidParameterValue if an invalid power state was specified.
        :raises: MissingParameterValue if required ipmi parameters are missing
        :raises: PowerStateFailure if the power couldn't be set to pstate.

        """
        driver_info = _parse_driver_info(task.node)

        if pstate == states.POWER_ON:
            driver_utils.ensure_next_boot_device(task, driver_info)
            _power_on(driver_info)
        elif pstate == states.POWER_OFF:
            _power_off(driver_info)
        else:
            raise exception.InvalidParameterValue(
                _("set_power_state called "
                  "with invalid power state %s.") % pstate)
        state = _power_status(driver_info)
        if state != pstate:
            raise exception.PowerStateFailure(pstate=pstate)

    @task_manager.require_exclusive_lock
    def reboot(self, task):
        """Cycles the power to the task's node.

        :param task: a TaskManager instance containing the node to act on.
        :raises: MissingParameterValue if required ipmi parameters are missing.
        :raises: InvalidParameterValue if an invalid power state was specified.
        :raises: PowerStateFailure if the final state of the node is not
            POWER_ON.

        """
        driver_info = _parse_driver_info(task.node)
        _power_off(driver_info)
        driver_utils.ensure_next_boot_device(task, driver_info)
        _power_on(driver_info)
        state = _power_status(driver_info)

        if state != states.POWER_ON:
            raise exception.PowerStateFailure(pstate=states.POWER_ON)


class RSCManagement(base.ManagementInterface):

    def get_properties(self):
        return COMMON_PROPERTIES

    def validate(self, task):
        """Check that 'driver_info' contains IPMI credentials.

        Validates whether the 'driver_info' property of the supplied
        task's node contains the required credentials information.

        :param task: a task from TaskManager.
        :raises: InvalidParameterValue if required IPMI parameters
            are missing.
        :raises: MissingParameterValue if a required parameter is missing.

        """
        _parse_driver_info(task.node)

    def get_supported_boot_devices(self, task):
        """Get a list of the supported boot devices.

        :param task: a task from TaskManager.
        :returns: A list with the supported boot devices defined
                  in :mod:`ironic.common.boot_devices`.

        """
        return [boot_devices.PXE, boot_devices.DISK]

    @task_manager.require_exclusive_lock
    def set_boot_device(self, task, device, persistent=False):
        """Set the boot device for the task's node.

        Set the boot device to use on next reboot of the node.

        :param task: a task from TaskManager.
        :param device: the boot device, one of
                       :mod:`ironic.common.boot_devices`.
        :param persistent: Boolean value. True if the boot device will
                           persist to all future boots, False if not.
                           Default: False.
        :raises: InvalidParameterValue if an invalid boot device is specified
        :raises: MissingParameterValue if required ipmi parameters are missing.
        :raises: IPMIFailure on an error from ipmitool.

        """
        if device != boot_devices.PXE:
            raise exception.InvalidParameterValue(_(
                "Invalid boot device %s specified, only pxe is support "
                "to set now") % device)

        driver_info = _parse_driver_info(task.node)

        address = driver_info.get('podm_address')
        node_id = driver_info.get('podm_node_id')

        url = 'http://%s:8181/v1/bootsource/%s/%s' % (address, node_id, device)
        requests.post(url, headers=_baseHeaders)

    @task_manager.require_exclusive_lock
    def destroy_node(self, task):
        _destroy_node(task.node)

    def get_boot_device(self, task):
        """Get the current boot device for the task's node.

        """
        driver_info = driver_info = _parse_driver_info(task.node)
        node = _node_detail(driver_info)
        boot = node.get('Boot')
        device = boot.get('BootSourceOverrideTarget')
        persistent = boot.get('BootSourceOverrideEnabled')
        response = {'boot_device': boot_devices.DISK, 'persistent': True}

        if device.lower() == boot_devices.PXE:
            response['boot_device'] = boot_devices.PXE

        if persistent == 'Once':
            response['persistent'] = False

        return response

    def get_sensors_data(self, task):
        return {}