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

import logging
import os

import flask
from oslo_utils import importutils
import requests
from requests import auth
from six.moves import http_client

from valence.api import link
from valence.common import constants
from valence.common import exception
from valence.common import utils
import valence.conf
from valence.redfish import tree


CONF = valence.conf.CONF
LOG = logging.getLogger(__name__)
SERVICE_ROOT = None

rsd_lib = importutils.try_import('rsd_lib')


def _parse_connection_info():
    base_url = CONF.podm.url
    username = CONF.podm.username
    password = CONF.podm.password
    root_prefix = CONF.podm.base_ext
    return {
        'base_url': base_url,
        'username': username,
        'password': password,
        'root_prefix': root_prefix
    }


def systems_list():
    """List systems contained by RSD Pod.

    :returns: List of systems in RSD Pod
    """
    conn_info = _parse_connection_info()
    conn = rsd_lib.RSDLib(conn_info['base_url'],
                          username=conn_info['username'],
                          password=conn_info['password'],
                          root_prefix=conn_info['root_prefix'])
    system_col = conn.get_system_collection()
    systems = system_col.get_members()

    systems_info = []
    for system in systems:
        systems_info.append({
            'identity': system.identity,
            'name': system.name,
            'power_state': system.power_state
        })
    return systems_info


def get_system(system_id):
    """Get specific system in RSD Pod.

    :param system_id: The ID for the system to retrieve
    :returns: Information about the system
    """
    conn_info = _parse_connection_info()
    conn = rsd_lib.RSDLib(conn_info['base_url'],
                          username=conn_info['username'],
                          password=conn_info['password'],
                          root_prefix=conn_info['root_prefix'])
    system_path = (conn_info['base_url'] +
                   conn_info['root_prefix'] +
                   'Systems/' + system_id)
    system = conn.get_system(system_path)

    system_info = {
        'asset_tag': system.asset_tag,
        'bios_version': system.bios_version,
        'boot_enabled': system.boot.enabled,
        'boot_mode': system.boot.mode,
        'boot_target': system.boot.target,
        'description': system.description,
        'hostname': system.hostname,
        'identity': system.identity,
        'indicator_led': system.indicator_led,
        'manufacturer': system.manufacturer,
        'name': system.name,
        'part_number': system.part_number,
        'power_state': system.power_state,
        'serial_number': system.serial_number,
        'sku': system.sku,
        'memory_health': system.memory_summary.health,
        'memory_size_gib': system.memory_summary.size_gib,
        'processor_count': system.processors.summary.count,
        'processor_architecture': system.processors.summary.architecture
    }

    return system_info


def update_service_root():
    global SERVICE_ROOT
    resp = send_request(CONF.podm.base_ext)
    SERVICE_ROOT = resp.json()


def get_rfs_url(serviceext):
    # Strip slash to make sure all input with/without slash
    redfish_base_ext = CONF.podm.base_ext.strip("/")
    serviceext = serviceext.strip("/")

    # Check whether serviceext statswith redfish_base_ext "redfish/v1", if yes,
    # use it as relative_url, otherwise add "redfish/v1" before it.
    if serviceext.startswith(redfish_base_ext):
        relative_url = serviceext
    else:
        relative_url = os.path.normpath(
            "/".join([redfish_base_ext, serviceext]))
    return requests.compat.urljoin(CONF.podm.url, relative_url)


def get_base_resource_url(resource, update_services=False):
    if update_services or not SERVICE_ROOT:
        LOG.debug("Updating service root...")
        update_service_root()
    resource_url = SERVICE_ROOT[resource]["@odata.id"]
    return resource_url


def send_request(resource, method="GET", **kwargs):
    # The verify=false param in the request should be removed eventually
    url = get_rfs_url(resource)
    httpuser = CONF.podm.username
    httppwd = CONF.podm.password
    resp = None
    LOG.debug(url)
    try:
        resp = requests.request(method, url, verify=False,
                                auth=requests.auth.HTTPBasicAuth(
                                    httpuser, httppwd),
                                **kwargs)
    except requests.exceptions.RequestException as e:
        LOG.error(e)
    return resp


def filter_chassis(jsonContent, filterCondition):
    returnMembers = []
    members = jsonContent['Members']
    for member in members:
        resource = member['@odata.id']
        resp = send_request(resource)
        member_detail = resp.json()
        chassisType = member_detail['ChassisType']
        if chassisType == filterCondition:
            returnMembers.append(member_detail)
    return returnMembers


def list_racks(filters={}, show_detail=False):
    chassis_url = get_base_resource_url("Chassis")
    resp = send_request(chassis_url)
    json_content = resp.json()
    raw_racks = filter_chassis(json_content, "Rack")
    racks = []
    filterPassed = True

    for rack in raw_racks:

        if any(filters):
            filterPassed = utils.match_conditions(rack, filters)
        if not filterPassed:
            continue

        rack_info = {}

        rack_id = rack["Id"]
        rack_name = rack["Name"]
        rack_systems = get_systems_in_chassis(rack)
        rack_info.update({"id": rack_id, "name": rack_name,
                          "systems": rack_systems})
        if show_detail:
            manufacturer = rack["Manufacturer"]
            model = rack["Model"]
            description = rack["Description"]
            serial_number = rack["SerialNumber"]
            rack_info.update({"manufacturer": manufacturer,
                              "model": model,
                              "description": description,
                              "serial_number": serial_number})
        racks.append(rack_info)
    return racks


def show_rack(rack_id):
    return list_racks({"Id": rack_id}, show_detail=True)


def get_systems_in_chassis(chassis, total_systems=[]):
    for chassis_link in chassis["Links"]["Contains"]:
        resp = send_request(chassis_link["@odata.id"])
        chassis = resp.json()
        total_systems = get_systems_in_chassis(chassis, total_systems)
    for system_link in chassis["Links"]["ComputerSystems"]:
        resp = send_request(system_link["@odata.id"])
        system = resp.json()
        if system["UUID"] not in total_systems:
            total_systems.append(system["UUID"])
    return total_systems


def pod_status(pod_url, username, password):
    try:
        resp = requests.get(pod_url,
                            auth=auth.HTTPBasicAuth(username, password))
        if resp.status_code == http_client.OK:
            return constants.PODM_STATUS_ONLINE
        else:
            return constants.PODM_STATUS_OFFLINE
    except requests.RequestException:
        return constants.PODM_STATUS_OFFLINE


def urls2list(url):
    # This will extract the url values from @odata.id inside Members
    resp = send_request(url)
    respdata = resp.json()
    if 'Members' in respdata:
        return [u['@odata.id'] for u in respdata['Members']]
    else:
        return []


def get_chassis_list():
    chassis_url = get_base_resource_url("Chassis")
    chassis_lnk_lst = urls2list(chassis_url)
    lst_chassis = []

    for clnk in chassis_lnk_lst:
        resp = send_request(clnk)
        data = resp.json()
        LOG.info(data)
        if "Links" in data:
            contains = []
            containedby = {}
            computersystems = []
            linksdata = data["Links"]
            if "Contains" in linksdata and linksdata["Contains"]:
                for c in linksdata["Contains"]:
                    contains.append(c['@odata.id'].split("/")[-1])

            if "ContainedBy" in linksdata and linksdata["ContainedBy"]:
                odata = linksdata["ContainedBy"]['@odata.id']
                containedby = odata.split("/")[-1]

            if "ComputerSystems" in linksdata and linksdata["ComputerSystems"]:
                for c in linksdata["ComputerSystems"]:
                    computersystems.append(c['@odata.id'])

            name = data["ChassisType"] + ":" + data["Id"]
            c = {"name": name,
                 "ChassisType": data["ChassisType"],
                 "ChassisID": data["Id"],
                 "Contains": contains,
                 "ContainedBy": containedby,
                 "ComputerSystems": computersystems}
            lst_chassis.append(c)
    return lst_chassis


def get_node_by_id(node_index, show_detail=True):
    """Get composed node details of specific index.

    :param node_index: numeric index of new composed node.
    :param show_detail: show more node detail when set to True.
    :returns: node detail info.
    """
    nodes_base_url = get_base_resource_url('Nodes')
    node_url = os.path.normpath('/'.join([nodes_base_url, node_index]))
    resp = send_request(node_url)

    LOG.debug(resp.status_code)
    if resp.status_code != http_client.OK:
        # Raise exception if don't find node
        raise exception.RedfishException(resp.json(),
                                         status_code=resp.status_code)

    respdata = resp.json()

    node_detail = {
        "name": respdata.get("Name"),
        "node_power_state": respdata.get("PowerState"),
        "links": [
            link.Link.make_link('self', flask.request.url_root,
                                'nodes/' + respdata.get("UUID"), '').as_dict(),
            link.Link.make_link('bookmark', flask.request.url_root,
                                'nodes/' + respdata.get("UUID"), '',
                                bookmark=True).as_dict()
        ]
    }

    if show_detail:
        node_detail.update({
            "index": node_index,
            "description": respdata.get("Description"),
            "node_state": respdata.get("ComposedNodeState"),
            "boot_source":
                respdata.get("Boot", {}).get("BootSourceOverrideTarget"),
            "target_boot_source":
                respdata.get("Boot", {}).get("BootSourceOverrideTarget"),
            "health_status": respdata.get("Status", {}).get("Health"),
            # TODO(lin.yang): "pooled_group_id" is used to check whether
            # resource can be assigned to composed node, which should be
            # supported after PODM API v2.1 released.
            "pooled_group_id": None,
            "computer_system": respdata.get("Links").get("ComputerSystem")
        })

    return node_detail


def build_hierarchy_tree():
    # builds the tree sturcture of the PODM data to get the location hierarchy
    lst_chassis = get_chassis_list()
    podmtree = tree.Tree()
    podmtree.add_node("0")  # Add root node
    for d in lst_chassis:
        podmtree.add_node(d["ChassisID"], d)

    for d in lst_chassis:
        containedby = d["ContainedBy"] if d["ContainedBy"] else "0"
        podmtree.add_node(d["ChassisID"], d, containedby)
        systems = d["ComputerSystems"]
        for system in systems:
            sysname = system.split("/")[-2] + ":" + system.split("/")[-1]
            podmtree.add_node(system, {"name": sysname}, d["ChassisID"])
    return podmtree


def compose_node(request_body):
    """Compose new node through podm api.

    :param request_body: The request content to compose new node, which should
                         follow podm format. Valence api directly pass it to
                         podm right now.
    :returns: The numeric index of new composed node.
    """

    # Get url of allocating resource to node
    nodes_url = get_base_resource_url('Nodes')
    resp = send_request(nodes_url, 'GET')
    if resp.status_code != http_client.OK:
        LOG.error('Unable to query ' + nodes_url)
        raise exception.RedfishException(resp.json(),
                                         status_code=resp.status_code)
    respdata = resp.json()
    allocate_url = respdata['Actions']['#ComposedNodeCollection.Allocate'][
        'target']

    # Allocate resource to this node
    LOG.debug('Allocating Node: {0}'.format(request_body))
    allocate_resp = send_request(allocate_url, 'POST',
                                 headers={'Content-type': 'application/json'},
                                 json=request_body)
    if allocate_resp.status_code != http_client.CREATED:
        # Raise exception if allocation failed
        raise exception.RedfishException(allocate_resp.json(),
                                         status_code=allocate_resp.status_code)

    # Allocated node successfully
    # node_url -- relative redfish url e.g redfish/v1/Nodes/1
    node_url = allocate_resp.headers['Location'].lstrip(CONF.podm.url)
    # node_index -- numeric index of new node e.g 1
    node_index = node_url.split('/')[-1]
    LOG.debug('Successfully allocated node:' + node_url)

    # Get url of assembling node
    resp = send_request(node_url, "GET")
    respdata = resp.json()
    assemble_url = respdata['Actions']['#ComposedNode.Assemble']['target']

    # Assemble node
    LOG.debug('Assembling Node: {0}'.format(assemble_url))
    assemble_resp = send_request(assemble_url, "POST")

    if assemble_resp.status_code != http_client.NO_CONTENT:
        # Delete node if assemble failed
        delete_composed_node(node_index)
        raise exception.RedfishException(assemble_resp.json(),
                                         status_code=resp.status_code)
    else:
        # Assemble successfully
        LOG.debug('Successfully assembled node: ' + node_url)

    # Return new composed node index
    return get_node_by_id(node_index)


def delete_composed_node(nodeid):
    nodes_url = get_base_resource_url("Nodes")
    delete_url = nodes_url + '/' + str(nodeid)
    resp = send_request(delete_url, "DELETE")
    if resp.status_code == http_client.NO_CONTENT:
        # we should return 200 status code instead of 204, because 204 means
        # 'No Content', the message in resp_dict will be ignored in that way
        return exception.confirmation(
            confirm_code="DELETED",
            confirm_detail="This composed node has been deleted successfully.")
    else:
        raise exception.RedfishException(resp.json(),
                                         status_code=resp.status_code)


def list_nodes():
    # list of nodes with hardware details needed for flavor creation

    # TODO(lin.yang): support filter when list nodes
    nodes = []
    nodes_url = get_base_resource_url("Nodes")
    node_url_list = urls2list(nodes_url)

    for url in node_url_list:
        node_index = url.split('/')[-1]
        nodes.append(get_node_by_id(node_index, show_detail=False))

    return nodes


def reset_node(nodeid, request):
    nodes_url = get_base_resource_url("Nodes")
    node_url = os.path.normpath("/".join([nodes_url, nodeid]))
    resp = send_request(node_url)

    if resp.status_code != http_client.OK:
        # Raise exception if don't find node
        raise exception.RedfishException(resp.json(),
                                         status_code=resp.status_code)

    node = resp.json()

    action_type = request.get("Reset", {}).get("Type")
    allowable_actions = node["Actions"]["#ComposedNode.Reset"][
        "ResetType@DMTF.AllowableValues"]

    if not action_type:
        raise exception.BadRequest(
            detail="The content of node action request is malformed. Please "
                   "refer to Valence api specification to correct it.")
    if allowable_actions and action_type not in allowable_actions:
        raise exception.BadRequest(
            detail="Action type '{0}' is not in allowable action list "
                   "{1}.".format(action_type, allowable_actions))

    target_url = node["Actions"]["#ComposedNode.Reset"]["target"]

    action_resp = send_request(target_url, 'POST',
                               headers={'Content-type': 'application/json'},
                               json={"ResetType": action_type})

    if action_resp.status_code != http_client.NO_CONTENT:
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


def set_boot_source(nodeid, request):
    nodes_url = get_base_resource_url("Nodes")
    node_url = os.path.normpath("/".join([nodes_url, nodeid]))
    resp = send_request(node_url)

    if resp.status_code != http_client.OK:
        # Raise exception if don't find node
        raise exception.RedfishException(resp.json(),
                                         status_code=resp.status_code)

    node = resp.json()

    boot_enabled = request.get("Boot", {}).get("Enabled")
    boot_target = request.get("Boot", {}).get("Target")
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

    action_resp = send_request(
        node_url, 'PATCH', headers={'Content-type': 'application/json'},
        json={"Boot": {"BootSourceOverrideEnabled": boot_enabled,
                       "BootSourceOverrideTarget": boot_target}})

    if action_resp.status_code != http_client.NO_CONTENT:
        raise exception.RedfishException(action_resp.json(),
                                         status_code=action_resp.status_code)
    else:
        # Set boot source successfully
        LOG.debug("Set boot source of composed node {0} to '{1}' with enabled "
                  "state '{2}' successfully."
                  .format(nodes_url, boot_target, boot_enabled))
        return exception.confirmation(
            confirm_code="Set Boot Source of Composed Node",
            confirm_detail="The boot source of composed node has been set to "
                           "'{0}' with enabled state '{1}' successfully."
                           .format(boot_target, boot_enabled))


def node_action(nodeid, request):
    # Only support one action in single request
    if len(list(request.keys())) != 1:
        raise exception.BadRequest(
            detail="No action found or multiple actions in one single request."
                   " Please refer to Valence api specification to correct the"
                   " content of node action request.")

    action = list(request.keys())[0]

    # Podm support two kinds of action for composed node, assemble and reset.
    # Because valence assemble node by default when compose node, so only need
    # to support "Reset" action here. In case podm new version support more
    # actions, use "functions" dict to drive the workflow.
    functions = {"Reset": reset_node,
                 "Boot": set_boot_source}

    if action not in functions:
        raise exception.BadRequest(
            detail="This node action '{0}' is unsupported. Please refer to "
                   "Valence api specification to correct this content of node "
                   "action request.".format(action))

    return functions[action](nodeid, request)
