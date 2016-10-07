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
from oslo_config import cfg
from oslo_log import log as logging
import requests
from requests.auth import HTTPBasicAuth
from rsc.common.redfish import tree

LOG = logging.getLogger(__name__)
cfg.CONF.import_group('podm', 'rsc.common.redfish.config')


def get_rfs_url(serviceext):
    REDFISH_BASE_EXT = "/redfish/v1/"
    INDEX = '' 
    # '/index.json'
    if REDFISH_BASE_EXT in serviceext:
        return cfg.CONF.podm.url + serviceext + INDEX
    else:
        return cfg.CONF.podm.url + REDFISH_BASE_EXT + serviceext + INDEX


def send_request(resource, method="GET",**kwargs):
    # The verify=false param in the request should be removed eventually
    url = get_rfs_url(resource)
    httpuser = cfg.CONF.podm.user
    httppwd = cfg.CONF.podm.password
    resp = None 
    try:
        resp = requests.request(method, url, verify=False, auth=HTTPBasicAuth(httpuser, httppwd), **kwargs)    
    except requests.exceptions.RequestException as e:
        LOG.error(e)
    return resp


def filter_chassis(jsonContent, filterCondition):
    returnJSONObj = {}
    returnMembers = []
    parsed = json.loads(jsonContent)
    members = parsed['Members']
    # count = parsed['Members@odata.count']
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
    # returnMembers = []
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


def get_details(source):
    # count = source['Members@odata.count']
    returnJSONObj = []
    members = source['Members']
    for member in members:
        resource = member['@odata.id']
        resp = send_request(resource)
        memberJson = resp.json()
        memberJsonObj = json.loads(memberJson)
        returnJSONObj[resource] = memberJsonObj
    return returnJSONObj


def systemdetails():
    returnJSONObj = []
    parsed = send_request('Systems')
    members = parsed['Members']
    for member in members:
        resource = member['@odata.id']
        resp = send_request(resource)
        memberJsonContent = resp.json()
        memberJSONObj = json.loads(memberJsonContent)
        returnJSONObj[resource] = memberJSONObj
    return(json.dumps(returnJSONObj))


def nodedetails():
    returnJSONObj = []
    parsed = send_request('Nodes')
    members = parsed['Members']
    for member in members:
        resource = member['@odata.id']
        resp = send_request(resource)
        memberJSONObj = resp.json()
        returnJSONObj[resource] = memberJSONObj
    return(json.dumps(returnJSONObj))


def podsdetails():
    jsonContent = send_request('Chassis')
    pods = filter_chassis(jsonContent, 'Pod')
    podsDetails = get_details(pods)
    return json.dumps(podsDetails)


def racksdetails():
    jsonContent = send_request('Chassis')
    racks = filter_chassis(jsonContent, 'Rack')
    racksDetails = get_details(racks)
    return json.dumps(racksDetails)


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
    return [u['@odata.id'] for u in respdata['Members']]


def extract_val(data, path):
    # function to select value at particularpath
    patharr = path.split("/")
    for p in patharr:
        data = data[p]
    return data


def node_cpu_details(nodeurl):
    cpucnt = 0
    cpuarch = ""
    cpulist = urls2list(nodeurl + '/Processors')
    for lnk in cpulist:
        LOG.info("Processing CPU %s" % lnk)
        resp = send_request(lnk)
        respdata = resp.json()
        cpucnt += extract_val(respdata, "TotalCores")
        cpuarch = extract_val(respdata, "InstructionSet")
        cpumodel = extract_val(respdata, "Model")
        LOG.debug(" Cpu details %s: %d: %s: %s "
                  % (nodeurl, cpucnt, cpuarch, cpumodel))
    return {"count": str(cpucnt), "arch": cpuarch, "model": cpumodel}


def node_ram_details(nodeurl):
    # this extracts the RAM and returns as dictionary
    resp = send_request(nodeurl)
    respjson = resp.json()
    ram = extract_val(respjson, "MemorySummary/TotalSystemMemoryGiB")
    #LOG.debug(" Total Ram for node %s : %d " % (nodeurl, ram))
    return str(ram) if ram else "0"


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
        for sd in hdds:
            if "CapacityBytes" in sd:
                if sd["CapacityBytes"] is not None:
                    storagecnt += sd["CapacityBytes"]
    LOG.debug("Total storage for node %s : %d " % (nodeurl, storagecnt))
    # to convert Bytes in to GB. Divide by 1073741824
    return str(storagecnt / 1073741824).split(".")[0]


def systems_list(count=None, filters={}):
    # comment the count value which is set to 2 now..
    # list of nodes with hardware details needed for flavor creation
    # count = 2
    lst_systems = []
    systemurllist = urls2list("Systems")
    podmtree = build_hierarchy_tree()
    #podmtree.writeHTML("0","/tmp/a.html")

    for lnk in systemurllist[:count]:
        filterPassed = True
        resp = send_request(lnk)
        system = resp.json()

        # this below code need to be changed when proper query mechanism
        # is implemented
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
        node = {"nodeid": systemid, "cpu": cpu,
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
            lst_systems.append(node)
        # LOG.info(str(node))
    return lst_systems


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


def get_nodebyid(nodeid):
    resp = send_request("Nodes/" + nodeid)
    return resp.json()


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

def compose_node(criteria={}):
    #node comosition
    composeurl = "Nodes/Actions/Allocate" 
    reqbody = None if not criteria else criteria
    headers = {'Content-type': 'application/json'}
    if not criteria:
        resp = send_request(composeurl, "POST", headers = headers) 
    else:
        resp = send_request(composeurl, "POST", json=criteria, headers = headers)
    LOG.info(resp.headers)
    LOG.info(resp.text)
    LOG.info(resp.status_code)
    composednode = resp.headers['Location']

    return { "node" : composednode }


def delete_composednode(nodeid):
    #delete composed node
    deleteurl = "Nodes/" + str(nodeid)
    resp = send_request(deleteurl, "DELETE")
    return resp

def nodes_list(count=None, filters={}):
    # comment the count value which is set to 2 now..
    # list of nodes with hardware details needed for flavor creation
    # count = 2
    lst_nodes = []
    nodeurllist = urls2list("Nodes")
    #podmtree = build_hierarchy_tree()
    #podmtree.writeHTML("0","/tmp/a.html")

    for lnk in nodeurllist:
        filterPassed = True
        resp = send_request(lnk)
        if resp.status_code != 200:
            Log.info("Error in fetching Node details " + lnk)
        else:
            node = resp.json()

            # this below code need to be changed when proper query mechanism
            # is implemented
            if any(filters):
                filterPassed = generic_filter(node, filters)
            if not filterPassed:
                continue

            nodeid = lnk.split("/")[-1]
            nodeuuid = node['UUID']
            nodelocation = node['AssetTag']
            #podmtree.getPath(lnk) commented as location should be computed using
            #other logic.consult Chester
            nodesystemurl = node["Links"]["ComputerSystem"]["@odata.id"]
            cpu = {}
            ram = 0
            nw = 0
            localstorage = node_storage_details(nodesystemurl)
            if "Processors" in node:
                cpu = { "count" : node["Processors"]["Count"],
                        "model" : node["Processors"]["Model"]}

            if "Memory" in node:
                ram = node["Memory"]["TotalSystemMemoryGiB"]

            if "EthernetInterfaces" in node["Links"]:
                nw = len(node["Links"]["EthernetInterfaces"])

            storage = 0
            bmcip = "127.0.0.1" #system['Oem']['Dell_G5MC']['BmcIp']
            bmcmac = "00:00:00:00:00" #system['Oem']['Dell_G5MC']['BmcMac']
            node = {"nodeid": nodeid, "cpu": cpu,
                    "ram": ram, "storage": localstorage,
                    "nw": nw, "location": nodelocation,
                    "uuid": nodeuuid, "bmcip": bmcip, "bmcmac": bmcmac}
            if filterPassed:
               lst_nodes.append(node)
               # LOG.info(str(node))
        return lst_nodes
