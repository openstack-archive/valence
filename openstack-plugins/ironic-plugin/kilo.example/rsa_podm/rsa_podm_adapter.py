# Copyright 2015 Lenovo
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
from utils import http
import constants
from compiler.ast import flatten
import rsa_resource_rest_template as default_data
from ironic import objects

_logger = logging.getLogger(__name__)

"""
pod manager wrapper to execute all the podm operations
"""


def get_podm_connection(context, ip, user, passwd):
    """
    get the pod manager connection by detail info
    """
    _logger.info('get the pod manager connection')
    podm_manager_api = PodManagerAPI(context, ip, user, passwd)
    _logger.info('end of getting the pod manager connection')
    return podm_manager_api


def get_podm_connection_by_node(context, node):
    """get the pod manager connection by node"""

    driver_info = node.driver_info
    ip = driver_info.get('podm_ip')
    user = driver_info.get('podm_username')
    passwd = driver_info.get('podm_password')
    podm_manager_api = PodManagerAPI(context, ip, user, passwd)
    # _logger.warn('end of getting the xclarity connection by node')
    return podm_manager_api


class PodManagerAPI(object):
    """Client for interacting with pod manager via a REST API."""

    def __init__(self, context, host, username, password, **kwargs):
        self.context = context
        self.host = host
        self.username = username
        self.password = password

        # Optional args
        self.auth = (self.username, self.password)
        self.domain = "https://%s:443" % self.host
        self.scheme = kwargs.pop('scheme', 'https')
        self.port = kwargs.pop('port', 443)
        self.verify = kwargs.pop('verify', False)
        self.retries = kwargs.pop('retries', 3)
        self.retry_interval = kwargs.pop('retry_interval', 2)

        # add pod_type
        self.pod_type = objects.PodManager.get_by_ip(context, host).type

    def get_resource_by_url(self, url):
        return http.do_get_request(url=url, auth=self.auth)

    def get_rack_list_by_pod_ip(self, ip):
        chassis_collection_url = "https://" + str(ip) + "/redfish/v1/Chassis"
        chassis_collection_info = http.do_get_request(
            url=chassis_collection_url, auth=self.auth)
        members = chassis_collection_info["Members"]  #
        rack_list = []
        for chassis in members:
            chassis_url = "https://" + str(ip) + chassis["@odata.id"]
            chassis_info = http.do_get_request(url=chassis_url, auth=self.auth)
            chassis_info.update(default_data.chassis)  #
            if chassis_info["ChassisType"] == "Rack":
                dic = dict()
                dic["name"] = chassis_info["Name"]
                dic["url"] = "https://" + str(ip) + chassis_info["@odata.id"]
                rack_list.append(dic)
        return rack_list

    def set_rsa_node_power_state(self, path, state):
        url = self.domain + path
        return http.do_post_request(url=url, auth=self.auth,
                                    body={"ResetType": state})

    def get_composed_node_list_info(self):
        return self.__parse_elements_from_collection_path(
            path='/redfish/v1/Nodes',
            default_data_value=default_data.composed_node)

    def get_computer_system_list_info(self):
        system_list = []
        systems_collection_url = self.domain + '/redfish/v1/Systems'
        systems_collection_info = http.do_get_request(
            url=systems_collection_url, auth=self.auth)
        for system in systems_collection_info['Members']:
            system_info = self.__get_computer_system_info(system['@odata.id'])
            system_list.append(system_info)
        return system_list

    def get_chassis_list(self, chassis_type=None):
        chassis_collection_url = self.domain + "/redfish/v1/Chassis"
        chassis_collection_info = http.do_get_request(
            url=chassis_collection_url, auth=self.auth)
        chassis_list = []
        for chassis in chassis_collection_info["Members"]:
            chassis_url = self.domain + chassis["@odata.id"]
            chassis_info = http.do_get_request(url=chassis_url, auth=self.auth)
            chassis_info = dict(default_data.chassis, **chassis_info)
            if chassis_type is None or chassis_info[
                "ChassisType"] == chassis_type:
                chassis_list.append(chassis_info)
        return chassis_list

    def get_drawers_list_info(self):
        return self.get_chassis_list(
            chassis_type=constants.CHASSIS_TYPE_DRAWER)

    def get_racks_list_info(self):
        return self.get_chassis_list(chassis_type=constants.CHASSIS_TYPE_RACK)

    def get_storage_list_info(self):
        if self.pod_type == "LENOVO-PODM":
            storage_service_path = "/redfish/v1/Chassis/PCIeSwitchChassis1"
            storage_service_list = []
            storage = http.do_get_request(
                url=self.domain + storage_service_path, auth=self.auth)
            storage_service_list.append(storage)
        else:
            storage_service_path = "/redfish/v1/Services/service1/Targets"
            storage_service_list = self.__parse_elements_from_collection_path(
                storage_service_path)

        return storage_service_list

    def get_volume_list_info(self):
        if self.pod_type == 'LENOVO-PODM':
            storage_service_path = \
                '/redfish/v1/Chassis/PCIeSwitchChassis1/StorageAdapters'
        else:
            storage_service_path = '/redfish/v1/Services'
        storage_service_list = self.__parse_elements_from_collection_path(
            storage_service_path)
        logical_drive_collection = []
        for storage in storage_service_list:
            logical_drive_collection_path = storage["LogicalDrives"][
                '@odata.id']
            logical_drive_collection = \
                self.__parse_elements_from_collection_path(
                    logical_drive_collection_path,
                    default_data_value=default_data.volume)
        return logical_drive_collection

    def get_volume_list_from_node(self):
        node_list = self.get_composed_node_list_info()
        volume_list = []
        for node in node_list:
            volume_list_path = node['Oem']['Lenovo:RackScale'][
                'ComposedLogicalDrives']
            for member in volume_list_path:
                volume_path = self.domain + member['@odata.id']
                volume = http.do_get_request(url=volume_path, auth=self.auth)
                volume_list.append(volume)
        return volume_list

    def get_ethernet_switches_list_info(self):
        switch_path = "/redfish/v1/EthernetSwitches"
        switch_list = self.__parse_elements_from_collection_path(switch_path)
        return switch_list

    def get_manager_list_info(self):
        manager_path = "/redfish/v1/Managers"
        manager_list = \
            self.__parse_elements_from_collection_path(manager_path,
                                                       default_data.manager)
        return manager_list

    #  ---------------- callable functions ----------------------------  #

    def __get_computer_system_info(self, path):
        computer_system_url = self.domain + path
        computer_system_info = http.do_get_request(url=computer_system_url,
                                                   auth=self.auth)
        system_info = dict(default_data.computer_system,
                           **computer_system_info)
        # fill cpu info
        cpus_path = system_info["Processors"]["@odata.id"]
        if len(cpus_path) > 1:
            system_info['cpus'] = self.__parse_elements_from_collection_path(
                cpus_path, default_data.processors)
        # fill memorys info
        mems_path = system_info["DimmConfig"]["@odata.id"]
        if len(mems_path) > 1:
            system_info[
                'memorys'] = self.__parse_elements_from_collection_path(
                mems_path, default_data.memory_dimm)
        # fill disks info
        vendor = "Intel" if self.pod_type == "LENOVO-PODM" else "Lenovo"
        adapter_collection_path = \
            system_info["Oem"][vendor + ":RackScale"]["Adapters"]["@odata.id"]
        if len(adapter_collection_path) > 1:
            system_info['disks'] = self.__get_disk_list_info_from_adapter_path(
                adapter_collection_path)
        # fill interface info
        interface_path = system_info["EthernetInterfaces"]["@odata.id"]
        if len(interface_path) > 1:
            system_info[
                'interfaces'] = self.__parse_elements_from_collection_path(
                interface_path)
        return system_info

    def __get_disk_list_info_from_adapter_path(self, path):
        disks = []
        if self.pod_type == "LENOVO-PODM":
            disks = self.__parse_elements_from_collection_path(
                path + "/Drives")
        else:  # INTEL-COMMON
            adapters = self.__parse_elements_from_collection_path(path)
            for adapter in adapters:
                device_collection_path = adapter['Devices']['@odata.id']
                devices = self.__parse_elements_from_collection_path(
                    device_collection_path, default_data.disk)
                disks.append(devices)
        return flatten(disks)

    def __parse_elements_from_collection_path(self, path,
                                              default_data_value=None):
        element_info_list = []
        collection_url = self.domain + path
        try:
            collection = http.do_get_request(url=collection_url,
                                             auth=self.auth)
        except Exception:
            collection = {}
        if collection:
            for element in collection["Members"]:
                element_url = self.domain + element["@odata.id"]
                element_info = http.do_get_request(url=element_url,
                                                   auth=self.auth)
                if default_data_value is not None:
                    element_info = dict(default_data_value, **element_info)
                element_info_list.append(element_info)
        return element_info_list
