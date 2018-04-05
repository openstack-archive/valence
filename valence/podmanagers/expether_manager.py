# Copyright (c) 2017 NEC, Corp.
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

import datetime
import logging

from oslo_utils import importutils
import requests

from valence.common import constants
from valence.common import exception
from valence.common import http_adapter as http
from valence.db import api as db_api

hwdata = importutils.try_import('hwdata', default=None)

# Free devices group_id
EEIO_DEFAULT_GID = '4093'
EESV_DEFAULT_GID = '4094'

# device_type (PCI Base Class Code)
type_SSD = 0x1
type_NIC = 0x2
type_GPU = 0x3
type_MULTI = 0x4
type_SERIAL = 0xC
type_USB = 0x3
type_ACS = 0x12
type_SWITCH = 0x6


LOG = logging.getLogger(__name__)


class ExpEtherManager(object):
    def __init__(self, username, password, url):
        self.url = url
        self.auth = requests.auth.HTTPBasicAuth(username, password)

    def _send_request_to_eem(self, query, method='get', **kwargs):
        """Prepare request and send it to EEM

        :param query: request URI of API
        :param method: method with which request is sent
        :param kwargs: additional values if any
        :return: response in json format
        """
        request_url = '/'.join([self.url, query])
        f = getattr(http, method)
        response = f(request_url, self.auth, **kwargs)
        self._handle_exceptions(response)
        return response.json()

    def compose_node(self, name, description, requirements):
        """Compose node according to flavor

        Attaches the devices as per the flavor specified and returns the
        EESV node information.

        :param name: name of node
        :param description: description if any
        :param requirements: format {'pci_device': {'type': ['NIC', 'SSD']}}
        :return: allocated node info as dict
        :raises: ExpEtherException , if eesv not available or requested device
                 is not available(e.g SSD)
        """
        # New key 'PCIDevice' is added to support ExpEther devices.

        # Get available EESV list and choose first available node
        # TODO(ramineni): work on load balancing part
        eesv_list = self._send_request_to_eem(
            query="devices?status=eesv")['devices']
        nodes_index = [node['index'] for node in
                       db_api.Connection.list_composed_nodes()]

        available_eesv = None
        for eesv in eesv_list:
            if eesv['id'] not in nodes_index:
                available_eesv = eesv
                break
        if available_eesv is None:
            LOG.exception("EESV node not available to compose a node")
            raise exception.ExpEtherException(status=404, code="40400",
                                              detail="Node not available")

        # Attach device according to flavor or properties in request
        if ('pci_device' in requirements and
                'type' in requirements['pci_device']):
            req_pci_type = requirements['pci_device']['type']
            for pci_type in req_pci_type:
                dev_filters = {'pooled_group_id': EEIO_DEFAULT_GID,
                               'type': pci_type}
                eeio_list = db_api.Connection.list_devices(dev_filters)
                if not eeio_list:
                    LOG.exception("Device type: %s not existing in database",
                                  pci_type)
                    raise exception.ExpEtherException(status=404, code="40400",
                                                      detail="Requested device"
                                                             " not available")

                self.attach(device_db=eeio_list[0],
                            node_index=available_eesv['id'])

        # If properties is empty, return the existing available eesv node.
        index = available_eesv['id']
        composed_node = {'name': name, 'index': index,
                         'resource_uri': 'devices/' + index}
        return composed_node

    def get_node_info(self, node_index):
        """To get existing eesv nodes details to manage it via valence

        :param node_index: EESV index
        :return: dict of eesv details
        """
        query = 'devices/' + node_index
        node_info = self._send_request_to_eem(query)['device']

        if node_info['status'] == 'eeio':
            LOG.exception("EEIO device id %s passed instead of eesv",
                          node_index)
            raise exception.ExpEtherException("Not a valid EESV node %s"
                                              % node_index)

        node_detail = {'name': node_info['id'],
                       'resource_uri': query,
                       'serial_number': node_info['serial_number'],
                       'power_state': node_info['power_status'],
                       'host_model': node_info['host_model'],
                       'host_serial_number': node_info['host_serial_number'],
                       'index': node_index,
                       'description': node_info['model'],
                       'type': node_info['type'],
                       'mac_address': node_info['mac_address'],
                       'pooled_group_id': node_info['group_id']
                       }
        return node_detail

    def delete_composed_node(self, node_id):
        """Delete composed node with respective node index

        Function it perform:-
        Detaches all connected devices to this node
        (updates group id of device in valence db and EEM to 4093)

        :param node_id: index of the node

        :raises ExpEtherException if detaching devices fails
        """
        try:
            self._detach_all_devices_from_node(node_id)
        except Exception as e:
            raise exception.ExpEtherException("Composed node %s deletion "
                                              "failed with error : %s"
                                              % (node_id, e.detail))

    def node_action(self, node_index, request):
        """Attaches and detaches device to a node

        :param node_index: eesv node index
        :param request: Contains type_of_action(attach or detach) and
                        resource_id
               Sample request:
                {"detach":
                   {"resource_id": "660a95b3-adaa-42d3-ac3f-dfe7ce6c9986"}}
        """
        # NOTE: type_of_action can be attach or detach
        action = list(request.keys())[0]
        if action not in ['attach', 'detach']:
            LOG.exception("Unsupported action: %s", action)
            raise exception.BadRequest(detail="Unsupported action: " + action)

        device_db = {}
        if request[action].get('resource_id'):
            device_uuid = request[action]['resource_id']
            device_db = db_api.Connection.get_device_by_uuid(
                device_uuid).as_dict()

        f = getattr(self, action, None)
        f(device_db, node_index)

    def systems_list(self, filters=None):
        """Retrieves list of all connected eesv systems

        :return: List of connected eesv's

        :raises ExpEtherException if unable to fetch system details
        """
        query = "devices/detail?status=eesv"
        try:
            results = []
            eesv_list = self._send_request_to_eem(query)['devices']
            for eesv in eesv_list:
                results.append(self._system_dict(eesv))
            return results

        except exception.ExpEtherException as e:
            message = "Listing eesv nodes failed with error: %s" % e.detail
            raise exception.ExpEtherException(code=e.code, detail=message,
                                              status=e.status)

    def get_system_by_id(self, system_id):
        """Get system detail by system_id provided by user

        :param system_id: User provided system_id
        :return: eesv node info

        :raises ExpEtherException if unable to fetch details
        """
        query = 'devices/' + system_id
        system = self._send_request_to_eem(query=query)['device']
        if system['status'] == 'eeio':
            LOG.exception("eeio device id %s passed instead of eesv",
                          system_id)
            raise exception.ExpEtherException("Not a valid EESV node %s"
                                              % system_id)
        update_time = self._convert_time_format(system['update_time'])
        system = {'id': system['id'],
                  'type': system['type'],
                  'pooled_group_id': system['group_id'],
                  'mac_address': system['mac_address'],
                  'serial_number': system['serial_number'],
                  'name': system['status'],
                  'power_state': system['power_status'],
                  'host_model': system['host_model'],
                  'host_serial_number': system['host_serial_number'],
                  'description': system['model'],
                  'ee_version': system['ee_version'],
                  'update_time': update_time
                  }
        return system

    def attach(self, device_db, node_index):
        """Attaches device to requested node

        Performs two actions:
        1) Sets group id of eeio device in EEM
        2) Updates device info in valence DB
        :param device_db: device info from valence DB
        :param node_index: EESV id to which device needs to be attached
        :raises BadRequest if devices is not free
        """
        LOG.debug("Attach device %s to node %s", device_db['uuid'],
                  node_index)
        device_id = device_db['properties']['device_id']
        if (device_db['node_id'] is not None or
                device_db['pooled_group_id'] != EEIO_DEFAULT_GID):
            raise exception.BadRequest(
                detail="Device %s already assigned to a different node: %s"
                       % (device_db['uuid'], device_db['node_id']))
        node_query = 'devices/' + node_index
        eesv = self._send_request_to_eem(node_query)['device']
        # Set group id of eesv if it is default
        if eesv['group_id'] == EESV_DEFAULT_GID:
            eesv['group_id'] = self._set_gid(device_id=node_index,
                                             group_id=None)['group_id']
            LOG.warning('Group ID of an EESV %s has been updated, a reboot'
                        'might be required for changes to take effect',
                        node_index)
        # Check if maximum number of devices are already connected to eesv
        max_eeio_count = eesv['max_eeio_count']
        query = "devices?status=eeio&group_id=" + eesv['group_id']
        eeio_list = self._send_request_to_eem(query)['devices']
        eeio_count = len(eeio_list)
        if eeio_count >= int(max_eeio_count):
            LOG.exception("Only %s devices that can be attached to node %s",
                          max_eeio_count, node_index)
            message = ("Node %s has already maximun number of devices attached"
                       % node_index)
            raise exception.ExpEtherException(title='Internal server error',
                                              detail=message, status=500)
        self._set_gid(device_id=device_id, group_id=eesv['group_id'])
        update_dev_info = {"pooled_group_id": eesv['group_id'],
                           "node_id": node_index,
                           "state": constants.DEVICE_STATES['ALLOCATED']
                           }
        db_api.Connection.update_device(device_db['uuid'], update_dev_info)

    def detach(self, device_db, node_index=None):
        """Detaches device from requested node

        Performs two function:
        1) Delete group id of eeio device in EEM
        2) Updates device group id in valence DB
        :param device_db: Valence DB entry of device which is to be updated
        :param node_index: None
        """
        LOG.debug("Detach device %s from node %s", device_db['uuid'],
                  node_index)
        device_id = device_db['properties']['device_id']
        device_uuid = device_db['uuid']
        if device_db['pooled_group_id'] == EEIO_DEFAULT_GID:
            LOG.debug("Device %s is not attached to any node" % device_uuid)
            return

        self._del_gid(device_id)
        update_dev_info = {"pooled_group_id": EEIO_DEFAULT_GID,
                           "node_id": None,
                           "state": constants.DEVICE_STATES['FREE']
                           }
        db_api.Connection.update_device(device_uuid, update_dev_info)

    def _handle_exceptions(self, response):
        """Handles exceptions from http requests

        :param response: output of the request
        :raises AuthorizationFailure: if invalid credentials are passed
                ExpEtherException: if any HTTPError occurs
        """
        if response.status_code == 401:
            raise exception.AuthorizationFailure("Invalid credentials passed")
        try:
            resp = response.json()
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            detail = resp['message']
            code = resp['code']
            LOG.exception(detail)
            raise exception.ExpEtherException(code=code, detail=detail,
                                              status=response.status_code)

    def _set_gid(self, device_id, group_id):
        """Updates the group id of the device

        Set the group id of EEIO device as of EESV to which it is going to
        connect.
        :param device_id: the device id on which group id is to updated
        :param group_id: group_id which is to be assigned
        :raises ExpEtherException if any HTTPError occurs
        """
        return self._send_request_to_eem("devices/" + device_id + "/group_id",
                                         'put', json={"group_id": group_id})

    def _del_gid(self, device_id):
        """Deletes the group id of the device

        Sends delete request to the url of device, which updates
        group id of device to 4093
        :param device_id: of device which is to be detached from node
        :raises ExpEtherException if any HTTPError occurs
        """
        return self._send_request_to_eem("devices/" + device_id + "/group_id",
                                         'delete')

    def _get_device_type(self, pci_code):
        """Gives device type based on its PCI code

        :param pci_code: PCI code of device from eem
        :return: type of device(e.g SSD, NIC)
        """
        class_code = int(pci_code, 0)
        c0 = class_code / (256 * 256)
        if c0 == type_NIC:
            return 'NIC'
        elif c0 == type_SSD:
            return 'SSD'
        elif c0 == type_GPU:
            return 'GPU'
        elif c0 == type_MULTI:
            return 'Multi'
        elif c0 == type_SERIAL:  # and ccode[1] == type_USB:
            return 'USB'
        elif c0 == type_ACS:
            return 'ACS'
        elif c0 == type_SWITCH:
            return 'SWITCH'
        else:
            return 'Unknown'

    def _detach_all_devices_from_node(self, node_id):
        """Detaches all devices from the node

        Fetches all connected devices to node, deletes group_id
        :param node_id: index of the node
        """
        db_dev_list = db_api.Connection.list_devices(
            filters={'node_id': node_id})
        for db_device in db_dev_list:
            self.detach(db_device)

    def get_status(self):
        """Checks ExpEtherManager Status

        Issues command to check version of EEM.
        :return: on or off status of pod_manager

        :raises AuthorizationFailure: if wrong credentials are passed
                ExpEtherException: if any HTTPError
        """
        error_message = "unable to reach podmanager at url: {} with error: {}"
        try:
            self._send_request_to_eem('api_version')
            return constants.PODM_STATUS_ONLINE
        # check for wrong ip and offline status
        except exception.AuthorizationFailure as e:
            raise exception.AuthorizationFailure(
                detail=error_message.format(self.url, e.detail))
        except exception.ExpEtherException as e:
            raise exception.ExpEtherException(
                code=e.code, detail=error_message.format(self.url, e.detail),
                status=e.status)

    def _system_dict(self, device):
        """Converts the resource details into desired dictionary format

        :param device: resource data from eem
        :return: Dictionary in desired format
        """

        system = {'id': device['id'],
                  'resource_uri': 'devices/' + device['id'],
                  'pooled_group_id': device['group_id'],
                  'type': device['type'],
                  'mac_address': device['mac_address'],
                  'host_serial_num': device['host_serial_number'],
                  'host_model': device['host_model']
                  }
        return system

    def _get_device_info(self, vendor_id, device_id):
        """Calculates vendor and device name

        Using python-hwdata retrieve information of 40G devices
        :param vendor_id: field 'pcie_vendor_id' value from EEM
        :param device_id: field 'pcie_device_id' value from EEM
        :return: Vendor and device name
        """
        vendor_name = ''
        device_name = ''
        if not hwdata:
            LOG.warning("hwdata module not available, unable to get the"
                        "vendor details")
            return vendor_name, device_name

        vendor_id = hex(int(vendor_id, 16))[2:].zfill(4)
        device_id = hex(int(device_id, 16))[2:].zfill(4)
        pci = hwdata.PCI()
        vendor_name = pci.get_vendor(vendor_id)
        device_name = pci.get_device(vendor_id, device_id)
        return vendor_name, device_name

    def get_all_devices(self):
        """Get all eeio devices connected to eem."""
        devices = []
        eeios = self._send_request_to_eem(query="devices/detail?status=eeio")
        for eeio in eeios['devices']:
            if eeio['notification_status0'][0] == 'down':
                continue
            extra = dict()
            state, eesv_id = self._check_eeio_state(eeio['group_id'])
            # If 40g, retreive device details, else None in case of 10g
            device_type = None
            if eeio["type"] == '40g':
                device_type = self._get_device_type(eeio["pcie_class_code"])
                vendor_name, device_name = self._get_device_info(
                    eeio["pcie_vendor_id"], eeio["pcie_device_id"])
                extra['vendor_name'] = vendor_name
                extra['device_name'] = device_name

            properties = dict()
            properties['device_id'] = eeio['id']
            properties['mac_address'] = eeio['mac_address']
            properties['model'] = eeio['type']

            values = {"type": device_type,
                      "pooled_group_id": eeio['group_id'],
                      "node_id": eesv_id,
                      "resource_uri": 'devices/' + eeio['id'],
                      "state": state,
                      "extra": extra,
                      "properties": properties,
                      }
            devices.append(values)
        return devices

    def _check_eeio_state(self, group_id):
        """Checks if eeio device is free or allocated to node

        :param group_id: pooled group id of device
        :return: state i.e allocated or free and eesv_id if allocated
        """
        state = constants.DEVICE_STATES['FREE']
        eesv_id = None
        if group_id != EEIO_DEFAULT_GID:
            state = constants.DEVICE_STATES['ALLOCATED']
            query = "devices?status=eesv&group_id=" + group_id
            result = self._send_request_to_eem(query)['devices']
            if result:
                eesv_id = result[0]['id']
        return state, eesv_id

    def get_ironic_node_params(self, node_info, **param):
        """Get ironic node params to register to ironic

        :param node_info: eesv node info
        :param param:
            Eg:{"driver_info":
                {"ipmi_address": "xxx.xxx.xx.xx",
                 "ipmi_username": "xxxxx",
                 "ipmi_password": "xxxxx"},

               "mac": "11:11:11:11:11:11",
               "driver": "agent_ipmitool"}
        :return: node and port arguments
        """
        driver = param.pop('driver', 'pxe_ipmitool')
        if not param.get('driver_info'):
            raise exception.ExpEtherException(
                detail='Missing driver_info in params %s' % node_info['uuid'],
                status=400)
        driver_info = param.pop('driver_info')

        node_args = {'name': node_info['name'],
                     'driver': driver,
                     'driver_info': driver_info}
        if param.get('mac', None):
            # MAC provided, create ironic ports
            port_args = {'address': param['mac']}
        return node_args, port_args

    @staticmethod
    def _convert_time_format(timestamp):
        """Convert time elapsed since 1/1/1970 to readable format

        :param timestamp: Update time from eem device
        :return: readable time format
        """
        value = int(timestamp)/1000.0
        return datetime.datetime.utcfromtimestamp(value).strftime(
            '%Y-%m-%d %H:%M:%S')
