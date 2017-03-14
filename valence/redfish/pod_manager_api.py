# copyright (c) 2016 Intel, Inc.
#
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

"""
Base API interface for Pod Manager
"""

from valence.common import http_adapter as http
from valence.controller import podmanagers


# local cache for pod manager connection
pod_manager_connections = {}


# local cache resource logic
def get_podm_connection(podm_db):
    podm_uuid = podm_db['uuid']
    if podm_uuid in pod_manager_connections:
        return pod_manager_connections[podm_uuid]

    podm_auth = podmanagers.get_basic_auth_from_authentication(
        podm_db['authentication'])
    podm_connection = Connection(podm_db['url'], podm_auth)
    pod_manager_connections[podm_uuid] = podm_connection
    return podm_connection


class Connection(object):
    """Base class for pod manager connections."""

    def __init__(self, podm_url, podm_auth):
        self.podm_url = podm_url
        self.podm_auth = podm_auth

    def get_pod_info(self):
        return http.get_http_request(self.podm_url, self.podm_auth)

    def list_nodes(self):
        nodes_collection_url = self.podm_url + '/Nodes'
        nodes_collection = http.get_http_request(nodes_collection_url,
                                                 self.podm_auth)

        node_list = []
        for member in nodes_collection['Members']:
            node_url = member["@odata.id"]
            node_info = http.get_http_request(node_url, self.podm_auth)
            node_list.append(node_info)

        return node_list

    def list_systems(self):
        systems_collection_url = self.podm_url + '/Systems'
        systems_collection = http.get_http_request(systems_collection_url,
                                                   self.podm_auth)

        system_list = []
        for member in systems_collection['Members']:
            system_url = member["@odata.id"]
            system_info = http.get_http_request(system_url, self.podm_auth)
            system_list.append(system_info)

        return system_list

    def list_storage(self):
        pass

    def list_racks(self):
        pass
