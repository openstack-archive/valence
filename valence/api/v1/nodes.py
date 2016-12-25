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

from flask import request
from flask_restful import abort
from flask_restful import Resource

from valence.common import utils
from valence.redfish import redfish

LOG = logging.getLogger(__name__)


class NodesList(Resource):

    def get(self):
        LOG.debug("GET /nodes")
        return redfish.nodes_list(request.args)

    def post(self):
        LOG.debug("POST /nodes/")
        return redfish.compose_node(request.get_json())


class NodesAction(Resource):

    # HTTP POST /nodes/
    def post(self, nodeid):
        # create a node management action such as ForceOff, On
        params = request.get_json()
        power_action = utils.extract_val(params, 'reset/type')
        resp = redfish.reset_node(nodeid, power_action)
        return resp


class Nodes(Resource):

    def get(self, nodeid):
        LOG.debug("GET /nodes/" + nodeid)
        return redfish.get_nodebyid(nodeid)

    def delete(self, nodeid):
        LOG.debug("DELETE /nodes/" + nodeid)
        return redfish.delete_composednode(nodeid)


class NodesStorage(Resource):

    def get(self, nodeid):
        LOG.debug("GET /nodes/%s/storage" % nodeid)
        return abort(501)
