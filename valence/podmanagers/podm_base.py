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


import rsd_lib

from rsd_lib.resources.node import constants as node_cons


class PodManagerBase(object):

    def __init__(self, username, password, podm_url):
        self.podm_url = podm_url
        self.driver = rsd_lib.RSDLib(podm_url,
                                     username=username,
                                     password=password)

    # TODO(ramineni): rebase on nate's patch
    def get_status(self):
        pass

    def get_podm_info(self):
        return self.driver.base

    def compose_node(self, request_body):
        return self.driver.compose_node(request_body)

    def get_node_list(self):
        return self.driver.get_node_collection()

    def get_node_info(self, node_id):
        return self.driver.get_node(node_id)

    def delete_composed_node(self, node_id):
        return self.driver.delete_compose_node(node_id)

    def reset_node(self, node_id, target_value):
        node = self.driver.get_node(node_id)
        if node:
            return node.reset_node(target_value)

    def set_node_boot_source(self, node_id, target_source,
                             enabled=node_cons.BOOT_SOURCE_ENABLED_ONCE,
                             mode=None):
        node = self.driver.get_node(node_id)
        if node:
            return node.set_node_boot_source(target_source, enabled, mode)

    # TODO(): use rsd_lib here
    def list_racks(self, filters={}, show_detail=False):
        pass

    def show_rack(self, rack_id):
        return self.driver.get_chassis(rack_id)

    # TODO(): use rsd_lib here
    def systems_list(self, filters={}):
        return self.driver.get_system_collection()

    def get_system_by_id(self, system_id):
        return self.driver.get_system(system_id)

    def get_storage_list(self):
        return self.driver.get_storage_service_collection()
