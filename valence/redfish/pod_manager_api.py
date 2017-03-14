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

import flask
import logging
import os

from valence.api import link
from valence.common import http_adapter as http
from valence.common import constants
from valence.common import exception
from valence.controller import podmanagers


LOG = logging.getLogger(__name__)

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

    def is_online(self):
        return self.__get_podm_status() == constants.PODM_STATUS_ONLINE

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

    def get_node_by_id(self, node_index, show_detail=True):
        """Get composed node details of specific index.

        :param node_index: numeric index of new composed node.
        :param show_detail: show more node detail when set to True.
        :returns: node detail info.
        """
        nodes_base_url = self.podm_url + '/Nodes'

        node_url = os.path.normpath('/'.join([nodes_base_url, node_index]))
        resp = http.get_http_request(node_url, self.podm_auth)

        LOG.debug(resp.status_code)
        if resp.status_code != http.OK:
            # Raise exception if don't find node
            raise exception.RedfishException(resp.json(),
                                             status_code=resp.status_code)

        respdata = resp.json()

        node_detail = {
            "name": respdata["Name"],
            "node_power_state": respdata["PowerState"],
            "links": [
                link.Link.make_link('self', flask.request.url_root,
                                    'nodes/' + respdata["UUID"], '').as_dict(),
                link.Link.make_link('bookmark', flask.request.url_root,
                                    'nodes/' + respdata["UUID"], '',
                                    bookmark=True).as_dict()
            ]
        }

        if show_detail:
            node_detail.update({
                "index": node_index,
                "description": respdata["Description"],
                "node_state": respdata["ComposedNodeState"],
                "boot_source": respdata["Boot"]["BootSourceOverrideTarget"],
                "target_boot_source": respdata["Boot"][
                    "BootSourceOverrideTarget"],
                "health_status": respdata["Status"]["Health"],
                # TODO(lin.yang): "pooled_group_id" is used to check whether
                # resource can be assigned to composed node, which should be
                # supported after PODM API v2.1 released.
                "pooled_group_id": None,
                "metadata": {
                    "processor": [self.show_cpu_details(i["@odata.id"])
                                  for i in respdata["Links"]["Processors"]],
                    "memory": [self.show_ram_details(i["@odata.id"])
                               for i in respdata["Links"]["Memory"]],
                    "network": [self.show_network_details(i["@odata.id"])
                                for i in
                                respdata["Links"]["EthernetInterfaces"]]
                }
            })

        return node_detail

    def compose_node(self, request_body):
        # Get url of allocating resource to node
        nodes_url = self.podm_url + '/Nodes'
        resp = http.get_http_request(url=nodes_url, http_auth=self.podm_auth)
        if resp.status_code != http.OK:
            LOG.error('Unable to query ' + nodes_url)
            raise exception.RedfishException(resp.json(),
                                             status_code=resp.status_code)
        respdata = resp.json()
        allocate_url = respdata['Actions']['#ComposedNodeCollection.Allocate'][
            'target']

        # Allocate resource to this node
        LOG.debug('Allocating Node: {0}'.format(request_body))
        header = {"Content-type": "application/json"}
        allocate_resp = http.post_http_request(url=allocate_url,
                                               http_auth=self.podm_auth,
                                               headers=header,
                                               json=request_body)
        if allocate_resp.status_code != http.CREATED:
            # Raise exception if allocation failed
            raise exception.RedfishException(allocate_resp.json(),
                                             status_code=allocate_resp.status_code)

        # Allocated node successfully
        # node_url -- relative redfish url e.g redfish/v1/Nodes/1
        node_url = allocate_resp.headers['Location'].lstrip(self.podm_url)
        # node_index -- numeric index of new node e.g 1
        node_index = node_url.split('/')[-1]
        LOG.debug('Successfully allocated node:' + node_url)

        # Get url of assembling node
        resp = http.get_http_request(url=node_url, http_auth=self.podm_auth)
        respdata = resp.json()
        assemble_url = respdata['Actions']['#ComposedNode.Assemble']['target']

        # Assemble node
        LOG.debug('Assembling Node: {0}'.format(assemble_url))
        assemble_resp = http.post_http_request(url=assemble_url,
                                               http_auth=self.podm_auth)

        if assemble_resp.status_code != http.NO_CONTENT:
            # Delete node if assemble failed
            self.delete_composed_node(node_index)
            raise exception.RedfishException(assemble_resp.json(),
                                             status_code=resp.status_code)
        else:
            # Assemble successfully
            LOG.debug('Successfully assembled node: ' + node_url)

        # Return new composed node index
        return self.get_node_by_id(node_index)

    def delete_composed_node(self, node_index_id):
        delete_node_url = self.podm_url + '/Nodes/' + str(node_index_id)
        resp = http.delete_http_request(url=delete_node_url,
                                        http_auth=self.podm_auth)
        if resp.status_code == http.NO_CONTENT:
            # we should return 200 status code instead of 204, because 204
            # means 'No Content', the message in resp_dict will be ignored i
            # n that way
            return exception.confirmation(
                confirm_code="DELETED",
                confirm_detail="This composed node has been deleted successfully.")
        else:
            raise exception.RedfishException(resp.json(),
                                             status_code=resp.status_code)

    def reset_node(self, node_id, action_type):
        node_url = self.podm_url + '/Nodes/' + node_id
        resp = http.get_http_request(node_url, self.podm_auth)

        if resp.status_code != http.OK:
            # Raise exception if don't find node
            raise exception.RedfishException(resp.json(),
                                             status_code=resp.status_code)

        node = resp.json()
        allowable_actions = node["Actions"]["#ComposedNode.Reset"][
            "ResetType@DMTF.AllowableValues"]

        if not action_type:
            raise exception.BadRequest(
                detail="The content of node action request is malformed. "
                       "Please refer to Valence api specification to correct "
                       "it.")
        if allowable_actions and action_type not in allowable_actions:
            raise exception.BadRequest(
                detail="Action type '{0}' is not in allowable action list "
                       "{1}.".format(action_type, allowable_actions))

        target_url = node["Actions"]["#ComposedNode.Reset"]["target"]

        action_resp = http.post_http_request(url=target_url,
                                             http_auth=self.podm_auth,
                                             hearders=constants.HTTP_HEADERS,
                                             json={"ResetType": action_type})
        if action_resp.status_code != http.NO_CONTENT:
            raise exception.RedfishException(action_resp.json(),
                                             status_code=action_resp.status_code)
        else:
            # Reset node successfully
            LOG.debug("Post action '{0}' to node {1} successfully."
                      .format(action_type, target_url))
            return exception.confirmation(
                confirm_code="Reset Composed Node",
                confirm_detail="This composed node has been set to '{0}' "
                               "successfully.".format(action_type))

    def set_node_boot_source(self, node_id, boot_enabled, boot_target):
        node_url = self.podm_url + '/Nodes/' + node_id

        resp = http.get_http_request(url=node_url, http_auth=self.podm_auth)
        if resp.status_code != http.OK:
            # Raise exception if don't find node
            raise exception.RedfishException(resp.json(),
                                             status_code=resp.status_code)
        node = resp.json()
        allowable_boot_target = \
            node["Boot"]["BootSourceOverrideTarget@Redfish.AllowableValues"]

        if not boot_enabled or not boot_target:
            raise exception.BadRequest(
                detail="The content of set boot source request is malformed. "
                       "Please refer to Valence api specification to correct it.")
        if boot_enabled not in ["Disabled", "Once", "Continuous"]:
            raise exception.BadRequest(
                detail="The parameter Enabled '{0}' is not in allowable list "
                       "['Disabled', 'Once', 'Continuous'].".format(
                    boot_enabled))
        if allowable_boot_target and \
                        boot_target not in allowable_boot_target:
            raise exception.BadRequest(
                detail="The parameter Target '{0}' is not in allowable list "
                       "{1}.".format(boot_target,
                                     allowable_boot_target))

        action_resp = http.patch_http_request(
            url=node_url,
            http_auth=self.podm_auth,
            headers=constants.HTTP_HEADERS,
            json={"Boot": {"BootSourceOverrideEnabled": boot_enabled,
                           "BootSourceOverrideTarget": boot_target}})

        if action_resp.status_code != http.NO_CONTENT:
            raise exception.RedfishException(action_resp.json(),
                                             status_code=action_resp.status_code)
        else:
            # Set boot source successfully
            LOG.debug(
                "Set boot source of composed node {0} to '{1}' with enabled "
                "state '{2}' successfully."
                .format(node_url, boot_target, boot_enabled))
            return exception.confirmation(
                confirm_code="Set Boot Source of Composed Node",
                confirm_detail="The boot source of composed node has been set "
                               "to '{0}' with enabled state '{1}' "
                               "successfully".format(boot_target, boot_enabled))

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

    def show_cpu_details(self, cpu_url):
        """Get processor details .

        :param cpu_url: relative redfish url to processor,
                        e.g /redfish/v1/Systems/1/Processors/1.
        :returns: dict of processor detail.
        """
        resp = http.get_http_request(cpu_url, self.podm_auth)
        if resp.status_code != http.OK:
            # Raise exception if don't find processor
            raise exception.RedfishException(resp.json(),
                                             status_code=resp.status_code)
        respdata = resp.json()
        cpu_details = {
            "instruction_set": respdata["InstructionSet"],
            "model": respdata["Model"],
            "speed_mhz": respdata["MaxSpeedMHz"],
            "total_core": respdata["TotalCores"]
        }

        return cpu_details

    def show_ram_details(self, ram_url):
        """Get memory details .

        :param ram_url: relative redfish url to memory,
                        e.g /redfish/v1/Systems/1/Memory/1.
        :returns: dict of memory detail.
        """
        resp = http.get_http_request(ram_url, self.podm_auth)
        if resp.status_code != http.OK:
            # Raise exception if don't find memory
            raise exception.RedfishException(resp.json(),
                                             status_code=resp.status_code)
        respdata = resp.json()
        ram_details = {
            "data_width_bit": respdata["DataWidthBits"],
            "speed_mhz": respdata["OperatingSpeedMHz"],
            "total_memory_mb": respdata["CapacityMiB"]
        }

        return ram_details

    def show_network_details(self, network_url):
        """Get network interface details .

        :param network_url: relative redfish url to network interface,
                        e.g /redfish/v1/Systems/1/EthernetInterfaces/1.
        :returns: dict of network interface detail.
        """
        resp = http.get_http_request(network_url, self.podm_auth)
        if resp.status_code != http.OK:
            # Raise exception if don't find network interface
            raise exception.RedfishException(resp.json(),
                                             status_code=resp.status_code)
        respdata = resp.json()
        network_details = {
            "speed_mbps": respdata["SpeedMbps"],
            "mac": respdata["MACAddress"],
            "status": respdata["Status"]["State"],
            "ipv4": [{
                         "address": ipv4["Address"],
                         "subnet_mask": ipv4["SubnetMask"],
                         "gateway": ipv4["Gateway"]
                     } for ipv4 in respdata["IPv4Addresses"]]
        }

        if respdata["VLANs"]:
            # Get vlan info
            vlan_url_list = self.__urls2list(respdata["VLANs"]["@odata.id"])
            network_details["vlans"] = []
            for url in vlan_url_list:
                vlan_info = http.get_http_request(url, self.podm_auth).json()
                network_details["vlans"].append({
                    "vlanid": vlan_info["VLANId"],
                    "status": vlan_info["Status"]["State"]
                })

        return network_details

    def __get_podm_status(self):
        try:
            resp = http.get_http_request(url=self.podm_url,
                                         http_auth=self.podm_auth)
            if resp.status_code == http.OK:
                return constants.PODM_STATUS_ONLINE
            else:
                return constants.PODM_STATUS_OFFLINE
        except Exception :
            return constants.PODM_STATUS_OFFLINE

    def __urls2list(self, url):
        # This will extract the url values from @odata.id inside Members
        resp = http.get_http_request(url, self.podm_auth)
        respdata = resp.json()
        if 'Members' in respdata:
            return [u['@odata.id'] for u in respdata['Members']]
        else:
            return []
