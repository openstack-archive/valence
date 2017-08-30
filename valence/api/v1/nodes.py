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

from flask import request
from flask_restful import abort
from flask_restful import Resource
from six.moves import http_client

from valence.common import utils
from valence.controller import nodes
from valence.validation import validator


class Nodes(Resource):

    def get(self):
        filter_args = request.args
        return utils.make_response(
            http_client.OK,
            nodes.Node.list_composed_nodes(filter_args.to_dict()))

    @validator.check_input('compose_node_schema')
    def post(self):
        # TODO(): podm_id should be passed in request body, if not passed
        # scheduler will decide on podm_id
        req = request.get_json()
        return utils.make_response(
            http_client.OK,
            nodes.Node(podm_id=req['podm_id']).compose_node(req))


class Node(Resource):

    def get(self, node_uuid):
        return utils.make_response(
            http_client.OK,
            nodes.Node(node_id=node_uuid).get_composed_node_by_uuid())

    def delete(self, node_uuid):
        return utils.make_response(
            http_client.OK,
            nodes.Node(node_id=node_uuid).delete_composed_node())


class NodeAction(Resource):

    @validator.check_input('node_action_schema')
    def post(self, node_uuid):
        return utils.make_response(
            http_client.NO_CONTENT,
            nodes.Node(node_id=node_uuid).node_action(request.get_json()))


class NodeManage(Resource):

    @validator.check_input('node_manage_schema')
    def post(self):
        req = request.get_json()
        return utils.make_response(
            http_client.OK,
            nodes.Node(podm_id=req['podm_id']).manage_node(req))


class NodesStorage(Resource):

    def get(self, nodeid):
        return abort(http_client.NOT_IMPLEMENTED)


class NodeRegister(Resource):

    def post(self, node_uuid):
        return utils.make_response(http_client.OK, nodes.Node.node_register(
                                   node_uuid, request.get_json()))
