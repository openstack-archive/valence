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

    def __init__(self, username, password, podm_url):
        self.podm_url = podm_url
        self.driver = sushy_instance.RedfishInstance(username=username,
                                                     password=password,
                                                     base_url=podm_url)

    def get_podm_info(self):
        return self.get_resource_info_by_url(self.podm_url)

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
