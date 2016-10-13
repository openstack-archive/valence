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

# This module is to add api to other services like PODS, RACKS..etc
# Since those will be a small class, all those are handled in a single class

from oslo_config import cfg
from oslo_log import log as logging
import pecan
from pecan import expose
from pecan import request
from pecan.rest import RestController
from valence.controller import api as controller_api

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class PodsController(RestController):

    def __init__(self, *args, **kwargs):
        super(PodsController, self).__init__(*args, **kwargs)

    # HTTP GET /nodes/
    @expose(template='json')
    def get_all(self, **kwargs):
        LOG.debug("GET /pods")
        rpcapi = controller_api.API(context=request.context)
        res = rpcapi.list_pods(filters=kwargs)
        return res

    @expose(template='json')
    def get(self, podid):
        LOG.debug("GET /pods" + podid)
        rpcapi = controller_api.API(context=request.context)
        node = rpcapi.get_podbyid(podid=podid)
        if not node:
            pecan.abort(404)
        return node


class RacksController(RestController):

    def __init__(self, *args, **kwargs):
        super(RacksController, self).__init__(*args, **kwargs)

    # HTTP GET /racks/
    @expose(template='json')
    def get_all(self, **kwargs):
        LOG.debug("GET /racks")
        rpcapi = controller_api.API(context=request.context)
        res = rpcapi.list_racks(filters=kwargs)
        return res

    @expose(template='json')
    def get(self, rackid):
        LOG.debug("GET /racks" + rackid)
        rpcapi = controller_api.API(context=request.context)
        node = rpcapi.get_rackbyid(rackid=rackid)
        if not node:
            pecan.abort(404)
        return node
