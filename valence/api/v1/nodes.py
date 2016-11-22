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

from flask import jsonify
from flask import make_response
from flask import request
from flask_restful import abort
from flask_restful import Resource

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

    _VALID_POWER_ACTION = ["On", "ForceOff", "GracefulRestart",
                           "ForceRestart", "Nmi", "ForceOn",
                           "PushPowerButton", "GracefulShutdown"
                           ]

    # HTTP POST /nodes/
    def post(self, nodeid):
        # create a node management action such as ForceOff, On
        params = request.get_json()
        power_action = None
        if params:
            reset_section = params.get("reset")
            if reset_section:
                power_action = reset_section.get('type')

        if power_action not in self._VALID_POWER_ACTION:
            reason = "unsupported reset type: '%s', the valid action" \
                     "is in: %s" % (power_action, self._VALID_POWER_ACTION)
            return make_response(jsonify(message=reason), 400)
        # make sure that the node exist, and get node detail
        node = None
        try:
            node = rfs.get_nodebyid(nodeid)
        except Exception as error:
            LOG.info(error)

        if not node:
            reason = 'unable to find the specified node: %s' % nodeid
            return make_response(jsonify(message=reason), 404)

        # TODO(yufei):Here we need to decide whether to accept the request
        # by the node's power status, for example, refuse to ForceOn a node
        # in running state
        resp = rfs.rest_node(nodeid, power_action)
        # rfs only return None when it get http exception
        if not resp:
            resp = make_response(jsonify(message='Internal Server Error'), 500)
        return resp


class NodesAction(Resource):

    _VALID_POWER_ACTION = ["On", "ForceOff", "GracefulRestart",
                           "ForceRestart", "Nmi", "ForceOn",
                           "PushPowerButton", "GracefulShutdown"
                           ]

    # HTTP POST /nodes/
    def post(self, nodeid):
        # create a node management action such as ForceOff, On
        params = request.get_json()
        power_action = None
        if params:
            reset_section = params.get("reset")
            if reset_section:
                power_action = reset_section.get('type')

        if power_action not in self._VALID_POWER_ACTION:
            reason = "unsupported reset type: '%s', the valid action" \
                     "is in: %s" % (power_action, self._VALID_POWER_ACTION)
            return make_response(jsonify(message=reason), 400)
        # make sure that the node exist, and get node detail
        node = None
        try:
            node = rfs.get_nodebyid(nodeid)
        except Exception as error:
            LOG.info(error)

        if not node:
            reason = 'unable to find the specified node: %s' % nodeid
            return make_response(jsonify(message=reason), 404)

        # TODO(yufei):Here we need to decide whether to accept the request
        # by the node's power status, for example, refuse to ForceOn a node
        # in running state
        resp = rfs.rest_node(nodeid, power_action)
        # rfs only return None when it get http exception
        if not resp:
            resp = make_response(jsonify(message='Internal Server Error'), 500)
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
