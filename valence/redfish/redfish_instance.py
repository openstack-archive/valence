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


from valence.common import http_adapter as http


class RedfishInstance(object):

    def __init__(self, http_auth):
        self.auth = http_auth

    def get_resources_by_url(self, resources_url):
        return http.get_http_request(url=resources_url,
                                     http_auth=self.auth)

    def compose_node(self, compose_url, redfish_compose_request):
        return http.post_http_request(url=compose_url,
                                      http_auth=self.auth,
                                      data=redfish_compose_request)

    def decompose(self, decompose_node_url):
        return http.post_http_request(url=decompose_node_url,
                                      http_auth=self.auth)
