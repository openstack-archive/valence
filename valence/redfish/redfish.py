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

import json
import logging
import os

import requests
from requests import auth
from six.moves import http_client

from valence.common import constants
from valence.common import exception
from valence.common import utils
from valence import config as cfg
from valence.redfish import tree


LOG = logging.getLogger(__name__)
SERVICE_ROOT = None


def update_service_root():
    global SERVICE_ROOT
    resp = send_request(cfg.redfish_base_ext)
    SERVICE_ROOT = resp.json()


def get_rfs_url(serviceext):
    # Strip slash to make sure all input with/without slash
    redfish_base_ext = cfg.redfish_base_ext.strip("/")
    serviceext = serviceext.strip("/")

    # Check whether serviceext statswith redfish_base_ext "redfish/v1", if yes,
    # use it as relative_url, otherwise add "redfish/v1" before it.
    if serviceext.startswith(redfish_base_ext):
        relative_url = serviceext
    else:
        relative_url = os.path.normpath(
            "/".join([redfish_base_ext, serviceext]))
    return requests.compat.urljoin(cfg.podm_url, relative_url)


def get_base_resource_url(resource, update_services=False):
    if update_services or not SERVICE_ROOT:
        LOG.debug("Updating service root...")
        update_service_root()
    resource_url = SERVICE_ROOT[resource]["@odata.id"]
    return resource_url


def send_request(resource, method="GET", **kwargs):
    # The verify=false param in the request should be removed eventually
    url = get_rfs_url(resource)
    httpuser = cfg.podm_user
    httppwd = cfg.podm_password
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
    returnJSONObj = {}
    returnMembers = []
    members = jsonContent['Members']
    for member in members:
        resource = member['@odata.id']
        resp = send_request(resource)
        memberJsonObj = resp.json()
        chassisType = memberJsonObj['ChassisType']
        if chassisType == filterCondition:
            returnMembers.append(member)
        returnJSONObj["Members"] = returnMembers
        returnJSONObj["Members@odata.count"] = len(returnMembers)
    return returnJSONObj


def racks():
    chassis_url = get_base_resource_url("Chassis")
    jsonContent = send_request(chassis_url)
    racks = filter_chassis(jsonContent, "Rack")
    return json.dumps(racks)


def pods():
    chassis_url = get_base_resource_url("Chassis")
    jsonContent = send_request(chassis_url)
    pods = filter_chassis(jsonContent, "Pod")
    return json.dumps(pods)


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


def system_cpu_details(system_url):
    cpucnt = 0
    cpuarch = ""
    cpumodel = ""
    cpulist = urls2list(system_url + '/Processors')
    for lnk in cpulist:
        LOG.info("Processing CPU %s" % lnk)
        resp = send_request(lnk)
        respdata = resp.json()
        # Check if CPU data is populated. It also may have NULL values
        cpucnt += utils.extract_val(respdata, "TotalCores", 0)
        cpuarch = utils.extract_val(respdata, "InstructionSet", "")
        cpumodel = utils.extract_val(respdata, "Model", "")
        LOG.debug(" Cpu details %s: %d: %s: %s "
                  % (system_url, cpucnt, cpuarch, cpumodel))
    return {"cores": str(cpucnt), "arch": cpuarch, "model": cpumodel}


def system_ram_details(system_url):
    # this extracts the RAM and returns as dictionary
    resp = send_request(system_url)
    respjson = resp.json()
    ram = utils.extract_val(respjson,
                            "MemorySummary/TotalSystemMemoryGiB", "0")
    return str(ram)


def system_network_details(system_url):
    # this extracts the total nw interfaces and returns as a string
    resp = send_request(system_url + "/EthernetInterfaces")
    respbody = resp.json()
    nwi = str(utils.extract_val(respbody, "Members@odata.count", "0"))
    LOG.debug(" Total NW for node %s : %s " % (system_url, nwi))
    return nwi


def system_storage_details(system_url):
    # this extracts the RAM and returns as dictionary
    storagecnt = 0
    hddlist = urls2list(system_url + "/SimpleStorage")
    for lnk in hddlist:
        resp = send_request(lnk)
        respbody = resp.json()
        devices = utils.extract_val(respbody, "Devices")
        if not devices:
            continue
        for device in devices:
            if "CapacityBytes" in device:
                if device["CapacityBytes"] is not None:
                    storagecnt += device["CapacityBytes"]
    LOG.debug("Total storage for system %s : %d " % (system_url, storagecnt))
    # to convert Bytes in to GB. Divide by 1073741824
    BYTES_PER_GB = 1073741824
    return str(storagecnt / BYTES_PER_GB).split(".")[0]


def systems_list(filters={}):
    # list of nodes with hardware details needed for flavor creation
    lst_systems = []
    systems_url = get_base_resource_url("Systems")
    systemurllist = urls2list(systems_url)
    podmtree = build_hierarchy_tree()
    LOG.info(systemurllist)
    for lnk in systemurllist:
        filterPassed = True
        resp = send_request(lnk)
        system = resp.json()

        if any(filters):
            filterPassed = utils.match_conditions(system, filters)
        if not filterPassed:
            continue

        systemid = lnk.split("/")[-1]
        systemuuid = system['UUID']
        systemlocation = podmtree.getPath(lnk)
        cpu = system_cpu_details(lnk)
        ram = system_ram_details(lnk)
        nw = system_network_details(lnk)
        storage = system_storage_details(lnk)
        system = {"id": systemid, "cpu": cpu,
                  "ram": ram, "storage": storage,
                  "nw": nw, "location": systemlocation,
                  "uuid": systemuuid}

        # filter based on RAM, CPU, NETWORK..etc
        if 'ram' in filters:
            filterPassed = (True
                            if int(ram) >= int(filters['ram'])
                            else False)

        # filter based on RAM, CPU, NETWORK..etc
        if 'nw' in filters:
            filterPassed = (True
                            if int(nw) >= int(filters['nw'])
                            else False)

        # filter based on RAM, CPU, NETWORK..etc
        if 'storage' in filters:
            filterPassed = (True
                            if int(storage) >= int(filters['storage'])
                            else False)

        if filterPassed:
            lst_systems.append(system)
    return lst_systems


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


def get_systembyid(systemid):
    return systems_list({"Id": systemid})


def get_nodebyid(nodeid):
    node = nodes_list({"Id": nodeid})
    if not node:
        raise exception.NotFound(detail='Node: %s not found' % nodeid)
    return node[0]


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
    nodes_url = get_base_resource_url('Nodes')
    headers = {'Content-type': 'application/json'}
    nodes_resp = send_request(nodes_url, 'GET', headers=headers)
    if nodes_resp.status_code != http_client.OK:
        LOG.error('Unable to query ' + nodes_url)
        raise exception.RedfishException(nodes_resp.json(),
                                         status_code=nodes_resp.status_code)
    nodes_json = json.loads(nodes_resp.content)
    allocate_url = nodes_json['Actions']['#ComposedNodeCollection.Allocate'][
        'target']
    resp = send_request(allocate_url, 'POST', headers=headers,
                        json=request_body)
    if resp.status_code == http_client.CREATED:
        allocated_node = resp.headers['Location']
        node_resp = send_request(allocated_node, "GET", headers=headers)
        LOG.debug('Successfully allocated node:' + allocated_node)
        node_json = json.loads(node_resp.content)
        assemble_url = node_json['Actions']['#ComposedNode.Assemble']['target']
        LOG.debug('Assembling Node: ' + assemble_url)
        assemble_resp = send_request(assemble_url, "POST", headers=headers)
        LOG.debug(assemble_resp.status_code)
        if assemble_resp.status_code == http_client.NO_CONTENT:
            LOG.debug('Successfully assembled node: ' + allocated_node)
            return {"node": allocated_node}
        else:
            parts = allocated_node.split('/')
            node_id = parts[-1]
            delete_composednode(node_id)
            raise exception.RedfishException(assemble_resp.json(),
                                             status_code=resp.status_code)
    else:
        raise exception.RedfishException(resp.json(),
                                         status_code=resp.status_code)


def delete_composednode(nodeid):
    nodes_url = get_base_resource_url("Nodes")
    delete_url = nodes_url + '/' + str(nodeid)
    resp = send_request(delete_url, "DELETE")
    if resp.status_code == http_client.NO_CONTENT:
        # we should return 200 status code instead of 204, because 204 means
        # 'No Content', the message in resp_dict will be ignored in that way
        resp_dict = exception.confirmation(confirm_detail="DELETED")
        return utils.make_response(http_client.OK, resp_dict)
    else:
        raise exception.RedfishException(resp.json(),
                                         status_code=resp.status_code)


def nodes_list(filters={}):
    # list of nodes with hardware details needed for flavor creation
    LOG.debug(filters)
    lst_nodes = []
    nodes_url = get_base_resource_url("Nodes")
    nodeurllist = urls2list(nodes_url)
    # podmtree = build_hierarchy_tree()
    # podmtree.writeHTML("0","/tmp/a.html")

    for lnk in nodeurllist:
        filterPassed = True
        resp = send_request(lnk)
        if resp.status_code != http_client.OK:
            LOG.info("Error in fetching Node details " + lnk)
        else:
            node = resp.json()

            if any(filters):
                filterPassed = utils.match_conditions(node, filters)
                LOG.info("FILTER PASSED" + str(filterPassed))
            if not filterPassed:
                continue

            nodeid = lnk.split("/")[-1]
            nodeuuid = node['UUID']
            nodelocation = node['AssetTag']
            # podmtree.getPath(lnk) commented as location should be
            # computed using other logic.consult Chester
            nodesystemurl = node["Links"]["ComputerSystem"]["@odata.id"]
            cpu = {}
            ram = 0
            nw = 0
            storage = system_storage_details(nodesystemurl)
            cpu = system_cpu_details(nodesystemurl)

            if "Memory" in node:
                ram = node["Memory"]["TotalSystemMemoryGiB"]

            if ("EthernetInterfaces" in node["Links"] and
                    node["Links"]["EthernetInterfaces"]):
                nw = len(node["Links"]["EthernetInterfaces"])

            bmcip = "127.0.0.1"  # system['Oem']['Dell_G5MC']['BmcIp']
            bmcmac = "00:00:00:00:00"  # system['Oem']['Dell_G5MC']['BmcMac']
            node = {"id": nodeid, "cpu": cpu,
                    "ram": ram, "storage": storage,
                    "nw": nw, "location": nodelocation,
                    "uuid": nodeuuid, "bmcip": bmcip, "bmcmac": bmcmac}

            # filter based on RAM, CPU, NETWORK..etc
            if 'ram' in filters:
                filterPassed = (True
                                if int(ram) >= int(filters['ram'])
                                else False)

            # filter based on RAM, CPU, NETWORK..etc
            if 'nw' in filters:
                filterPassed = (True
                                if int(nw) >= int(filters['nw'])
                                else False)

            # filter based on RAM, CPU, NETWORK..etc
            if 'storage' in filters:
                filterPassed = (True
                                if int(storage) >= int(filters['storage'])
                                else False)

            if filterPassed:
                lst_nodes.append(node)
    return lst_nodes
