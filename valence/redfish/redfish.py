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
import requests
from requests.auth import HTTPBasicAuth
from valence import config as cfg
from valence.redfish import tree


LOG = logging.getLogger(__name__)


def get_rfs_url(serviceext):
    REDFISH_BASE_EXT = "/redfish/v1/"
    INDEX = ''
    # '/index.json'
    if REDFISH_BASE_EXT in serviceext:
        return cfg.podm_url + serviceext + INDEX
    else:
        return cfg.podm_url + REDFISH_BASE_EXT + serviceext + INDEX


def send_request(resource, method="GET", **kwargs):
    # The verify=false param in the request should be removed eventually
    url = get_rfs_url(resource)
    httpuser = cfg.podm_user
    httppwd = cfg.podm_password
    resp = None
    LOG.debug(url)
    try:
        resp = requests.request(method, url, verify=False,
                                auth=HTTPBasicAuth(httpuser, httppwd),
                                **kwargs)
    except requests.exceptions.RequestException as e:
        LOG.error(e)
    return resp


def filter_chassis(jsonContent, filterCondition):
    returnJSONObj = {}
    returnMembers = []
    parsed = json.loads(jsonContent)
    members = parsed['Members']
    for member in members:
        resource = member['@odata.id']
        resp = send_request(resource)
        memberJsonObj = json.loads(resp.json())
        chassisType = memberJsonObj['ChassisType']
        if chassisType == filterCondition:
            returnMembers.append(member)
        returnJSONObj["Members"] = returnMembers
        returnJSONObj["Members@odata.count"] = len(returnMembers)
    return returnJSONObj


def generic_filter(jsonContent, filterConditions):
    # returns boolean based on filters..its generic filter
    is_filter_passed = False
    for fc in filterConditions:
        if fc in jsonContent:
            if jsonContent[fc].lower() == filterConditions[fc].lower():
                is_filter_passed = True
            else:
                is_filter_passed = False
            break
        elif "/" in fc:
            querylst = fc.split("/")
            tmp = jsonContent
            for q in querylst:
                tmp = tmp[q]
            if tmp.lower() == filterConditions[fc].lower():
                is_filter_passed = True
            else:
                is_filter_passed = False
            break
        else:
            LOG.warn(" Filter string mismatch ")
    LOG.info(" JSON CONTENT " + str(is_filter_passed))
    return is_filter_passed


def racks():
    jsonContent = send_request('Chassis')
    racks = filter_chassis(jsonContent, 'Rack')
    return json.dumps(racks)


def pods():
    jsonContent = send_request('Chassis')
    pods = filter_chassis(jsonContent, 'Pod')
    return json.dumps(pods)


def urls2list(url):
    # This will extract the url values from @odata.id inside Members
    resp = send_request(url)
    respdata = resp.json()
    if 'Members' in respdata:
        return [u['@odata.id'] for u in respdata['Members']]
    else:
        return []


def extract_val(data, path, defaultval=None):
    # function to select value at particularpath
    patharr = path.split("/")
    for p in patharr:
        data = data[p]
    data = (data if data else defaultval)
    return data


def node_cpu_details(nodeurl):
    cpucnt = 0
    cpuarch = ""
    cpumodel = ""
    cpulist = urls2list(nodeurl + '/Processors')
    for lnk in cpulist:
        LOG.info("Processing CPU %s" % lnk)
        resp = send_request(lnk)
        respdata = resp.json()
        # Check if CPU data is populated. It also may have NULL values
        cpucnt += extract_val(respdata, "TotalCores", 0)
        cpuarch = extract_val(respdata, "InstructionSet", "")
        cpumodel = extract_val(respdata, "Model", "")
        LOG.debug(" Cpu details %s: %d: %s: %s "
                  % (nodeurl, cpucnt, cpuarch, cpumodel))
    return {"cores": str(cpucnt), "arch": cpuarch, "model": cpumodel}


def node_ram_details(nodeurl):
    # this extracts the RAM and returns as dictionary
    resp = send_request(nodeurl)
    respjson = resp.json()
    ram = extract_val(respjson, "MemorySummary/TotalSystemMemoryGiB", "0")
    return str(ram)


def node_nw_details(nodeurl):
    # this extracts the total nw interfaces and returns as a string
    resp = send_request(nodeurl + "/EthernetInterfaces")
    respbody = resp.json()
    nwi = extract_val(respbody, "Members@odata.count")
    LOG.debug(" Total NW for node %s : %d " % (nodeurl, nwi))
    return str(nwi) if nwi else "0"


def node_storage_details(nodeurl):
    # this extracts the RAM and returns as dictionary
    storagecnt = 0
    hddlist = urls2list(nodeurl + "/SimpleStorage")
    for lnk in hddlist:
        resp = send_request(lnk)
        respbody = resp.json()
        hdds = extract_val(respbody, "Devices")
        if not hdds:
            continue
        for sd in hdds:
            if "CapacityBytes" in sd:
                if sd["CapacityBytes"] is not None:
                    storagecnt += sd["CapacityBytes"]
    LOG.debug("Total storage for node %s : %d " % (nodeurl, storagecnt))
    # to convert Bytes in to GB. Divide by 1073741824
    return str(storagecnt / 1073741824).split(".")[0]


def systems_list(filters={}):
    # list of nodes with hardware details needed for flavor creation
    lst_systems = []
    systemurllist = urls2list("Systems")
    podmtree = build_hierarchy_tree()
    LOG.info(systemurllist)
    for lnk in systemurllist:
        filterPassed = True
        resp = send_request(lnk)
        system = resp.json()

        if any(filters):
            filterPassed = generic_filter(system, filters)
        if not filterPassed:
            continue

        systemid = lnk.split("/")[-1]
        systemuuid = system['UUID']
        systemlocation = podmtree.getPath(lnk)
        cpu = node_cpu_details(lnk)
        ram = node_ram_details(lnk)
        nw = node_nw_details(lnk)
        storage = node_storage_details(lnk)
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


def storage_services_list():
    service_list = []
    service_url_list = urls2list("Services")
    for url in service_url_list:
        resp = send_request(url)
        service = resp.json()
        service_list.append(service)
    return service_list


def pooled_storage_list(filters=None, show_details=False):
    if filters == None:
        filters = {}
    pooled_storage_drives = []
    services = storage_services_list()
    for service in services:
        filterPassed = True
        drives_url_list = urls2list(service["LogicalDrives"]["@odata.id"])
        for url in drives_url_list:
            resp = send_request(url)
            pooled_storage_drive = resp.json()
            if any(filters):
                filterPassed = generic_filter(pooled_storage_drive, filters)
            if not filterPassed:
                continue

            drive_name = pooled_storage_drive["Name"]
            drive_description = pooled_storage_drive["Description"]
            drive_id = pooled_storage_drive["Id"]

            drive = {"Name": drive_name, "Description": drive_description,
                     "id": drive_id}

            if show_details:
                drive_capacity = pooled_storage_drive["CapacityGiB"]
                drive_type = pooled_storage_drive["Type"]
                drive_mode = pooled_storage_drive["Mode"]
                drive_health = pooled_storage_drive["Status"]["Health"]
                drive.update({"capacity": drive_capacity,
                              "type": drive_type, "mode": drive_mode,
                              "health": drive_health})

            pooled_storage_drives.append(drive)
    return pooled_storage_drives


def get_chassis_list():
    chassis_lnk_lst = urls2list("Chassis")
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
    return nodes_list({"Id": nodeid})


def get_drive_by_id(driveid):
    return pooled_storage_list({"Id": driveid}, True)


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


def compose_node(data):
    composeurl = "Nodes/Actions/Allocate"
    headers = {'Content-type': 'application/json'}
    criteria = data["criteria"]
    if not criteria:
        resp = send_request(composeurl, "POST", headers=headers)
    else:
        resp = send_request(composeurl, "POST", json=criteria, headers=headers)

    composednode = resp.headers['Location']
    return {"node": composednode}


def delete_composednode(nodeid):
    deleteurl = "Nodes/" + str(nodeid)
    resp = send_request(deleteurl, "DELETE")
    return resp


def nodes_list(filters={}):
    # list of nodes with hardware details needed for flavor creation
    LOG.debug(filters)
    lst_nodes = []
    nodeurllist = urls2list("Nodes")
    # podmtree = build_hierarchy_tree()
    # podmtree.writeHTML("0","/tmp/a.html")

    for lnk in nodeurllist:
        filterPassed = True
        resp = send_request(lnk)
        if resp.status_code != 200:
            LOG.info("Error in fetching Node details " + lnk)
        else:
            node = resp.json()

            if any(filters):
                filterPassed = generic_filter(node, filters)
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
            storage = node_storage_details(nodesystemurl)
            cpu = node_cpu_details(lnk)

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
