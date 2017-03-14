#!/usr/bin/env python
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

import requests

from valence.redfish.redfish_instance import RedfishInstance


class PodManagerBase(object):

    def __init__(self, username, password, podm_url):
        self.podm_auth = requests.auth.HTTPBasicAuth(username, password)
        self.podm_url = podm_url
        self.redfish = RedfishInstance(self.podm_auth)

    def get_podm_info(self):

        return self.get_resource_info_by_url(self.podm_url)

    def get_resource_info_by_url(self, resource_url):
        return self.redfish.get_resources_by_url(resource_url)

    def get_chassis_collection(self):
        chassis_collection_url = self.podm_url + '/Chassis'
        return self.redfish.get_resources_by_url(chassis_collection_url)

    def get_chassis_info(self, chassis_id):
        chassis_url = self.podm_url + '/Chassis/' + chassis_id
        return self.redfish.get_resources_by_url(chassis_url)

    def compose_new_node(self, podm_compose_request_body):
        compose_url = self.podm_url + '/Nodes/Actions/Allocate'
        redfish_compose_node_request_body = podm_compose_request_body # TODO
        return self.redfish.compose_node(compose_url,
                                         redfish_compose_node_request_body)

    def decompose_node(self, node_url):
        return self.redfish.decompose(node_url)
