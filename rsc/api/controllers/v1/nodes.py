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

from oslo_config import cfg
from oslo_log import log as logging
import pecan
from pecan import expose
from pecan import request
from pecan import response
from pecan.rest import RestController
from rsc.controller import api as controller_api

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


#class NodeDetailController(object):
class NodeDetailController(RestController):
    def __init__(self, nodeid):
        self.nodeid = nodeid

    # HTTP GET /nodes/
    @expose()
    def delete(self):
        LOG.debug("DELETE /nodes")
        rpcapi = controller_api.API(context=request.context)
        res = rpcapi.delete_composednode(nodeid=self.nodeid)
        LOG.info(str(res))
        return res 

    @expose()
    def storages(self):
        pecan.abort(501, "/nodes/node id/storages")


class NodesController(RestController):

    def __init__(self, *args, **kwargs):
        super(NodesController, self).__init__(*args, **kwargs)

    # HTTP GET /nodes/
    @expose(template='json')
    def get_all(self, **kwargs):
        LOG.debug("GET /nodes")
        rpcapi = controller_api.API(context=request.context)
        res = rpcapi.list_nodes(filters=kwargs)
        return res

    # HTTP GET /nodes/
#    @index.when(method='POST', template='json')
    @expose(template='json')
    def post(self, **kwargs):
        LOG.debug("POST /nodes")
        rpcapi = controller_api.API(context=request.context)
        res = rpcapi.compose_nodes(criteria=kwargs)
        return res

    @expose(template='json')
    def get(self, nodeid):
        LOG.debug("GET /nodes" + nodeid)
        rpcapi = controller_api.API(context=request.context)
        node = rpcapi.get_nodebyid(nodeid=nodeid)
        if not node:
            pecan.abort(404)
        return node

    @expose()
    def _lookup(self, nodeid, *remainder):
        # node  = get_student_by_primary_key(primary_key)
        if nodeid:
            return NodeDetailController(nodeid), remainder
        else:
            pecan.abort(404)
