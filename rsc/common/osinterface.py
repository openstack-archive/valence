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


LOG = logging.getLogger(__name__)
cfg.CONF.import_group('undercloud', 'rsc.controller.config')


def _send_request(url, method, headers, requestbody=None):
    defaultheaders = {'Content-Type': 'application/json'}
    auth = HTTPBasicAuth(cfg.CONF.undercloud.os_user,
                         cfg.CONF.undercloud.os_password)
    headers = defaultheaders.update(headers)
    LOG.debug(url)
    resp = requests.request(method,
                            url,
                            headers=defaultheaders,
                            data=requestbody,
                            auth=auth)
    LOG.debug(resp.status_code)
    return resp.json()


def _get_servicecatalogue_endpoint(keystonejson, servicename):
    """Fetch particular endpoint from Keystone.

       This function is to get the particular endpoint from the
       list of endpoints returned fro keystone.

    """

    for d in keystonejson["access"]["serviceCatalog"]:
        if(d["name"] == servicename):
            return d["endpoints"][0]["publicURL"]


def _get_token_and_url(nameofendpoint):
    """Fetch token from the endpoint

    This function get new token and associated endpoint.
    name of endpoint carries the name of the service whose
    endpoint need to be found.

    """

    url = cfg.CONF.undercloud.os_admin_url + "/tokens"
    data = {"auth":
            {"tenantName": cfg.CONF.undercloud.os_tenant,
             "passwordCredentials":
             {"username": cfg.CONF.undercloud.os_user,
              "password": cfg.CONF.undercloud.os_password}}}
    rdata = _send_request(url, "POST", {}, json.dumps(data))
    tokenid = rdata["access"]["token"]["id"]
    endpoint = _get_servicecatalogue_endpoint(rdata, nameofendpoint)
    LOG.debug("Token,Endpoint %s: %s from keystone for %s"
              % (tokenid, endpoint, nameofendpoint))
    return (tokenid, endpoint)


# put this function in utils.py later
def _get_imageid(jsondata, imgname):
    # write a generic funciton for this and _get_servicecatalogue_endpoint
    for d in jsondata["images"]:
        if(d["name"] == imgname):
            return d["id"]


def get_undercloud_images():
    tokenid, endpoint = _get_token_and_url("glance")
    resp = _send_request(endpoint + "/v2/images",
                         "GET",
                         {'X-Auth-Token': tokenid})
    imagemap = {"deploy_ramdisk": _get_imageid(resp, "bm-deploy-ramdisk"),
                "deploy_kernel": _get_imageid(resp, "bm-deploy-kernel"),
                "image_source": _get_imageid(resp, "overcloud-full"),
                "ramdisk": _get_imageid(resp, "overcloud-full-initrd"),
                "kernel": _get_imageid(resp, "overcloud-full-vmlinuz")}
    return imagemap
