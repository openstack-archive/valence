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

from valence.redfish.sushy import sushy_instance


class PodManagerBase(object):

    def __init__(self, username, password, podm_url, **kwargs):
        self.podm_url = podm_url
        self.username = username
        self.password = password
        self.driver = sushy_instance.RedfishInstance(username=username,
                                                     password=password,
                                                     base_url=podm_url)

    # TODO(): use rsd_lib here
    def get_status(self):
        pass

    def get_podm_info(self):
        return self.get_resource_info_by_url(self.podm_url)

    # TODO(): use rsd_lib here
    def compose_node(self, name, description, requirements):
        pass

    # TODO(): use rsd_lib here
    def delete_composed_node(self, node_id):
        pass

    # TODO(): use rsd_lib here
    def node_action(self, index, request_body):
        pass

    # TODO(): use rsd_lib here
    def list_racks(self, filters={}, show_detail=False):
        pass

    # TODO(): use rsd_lib here
    def show_rack(self, rack_id):
        pass

    # TODO(): use rsd_lib here
    def systems_list(self, filters={}):
        pass

    # TODO(): use rsd_lib here
    def get_system_by_id(self, system_id):
        pass

    # TODO(): to be implemented in rsb_lib
    def get_all_devices(self):
        pass

    def get_ironic_node_params(self, node_info, **param):
        # TODO(): change to 'rsd' once ironic driver is implemented.
        driver_info = {
            'redfish_address': self.podm_url,
            'redfish_username': self.username,
            'redfish_password': self.password,
            'redfish_system_id': node_info['computer_system']
        }
        node_args = {}
        if param and param.get('driver_info', None):
            driver_info.update(param.pop('driver_info'))

        node_args.update({'driver': 'redfish', 'name': node_info['name'],
                          'driver_info': driver_info})
        port_args = {'address': node_info['metadata']['network'][0]['mac']}

        # update any remaining params passed
        if param:
            node_args.update(param)

        return node_args, port_args

    def get_resource_info_by_url(self, resource_url):
        return self.driver.get_resources_by_url(resource_url)

    def get_chassis_collection(self):
        chassis_collection_url = self.podm_url + '/Chassis'
        return self.driver.get_resources_by_url(chassis_collection_url)

    def get_chassis_info(self, chassis_id):
        chassis_url = self.podm_url + '/Chassis/' + chassis_id
        return self.driver.get_resources_by_url(chassis_url)

    def get_system_collection(self):
        system_collection_url = self.podm_url + '/Systems'
        return self.driver.get_resources_by_url(system_collection_url)

    def get_system_info(self, system_id):
        system_url = self.podm_url + '/Systems/' + system_id
        return self.driver.get_resources_by_url(system_url)

    def get_node_collection(self):
        node_collection_url = self.podm_url + '/Nodes'
        return self.driver.get_resources_by_url(node_collection_url)

    def get_node_info(self, node_id):
        node_url = self.podm_url + '/Nodes/' + node_id
        return self.driver.get_resources_by_url(node_url)
