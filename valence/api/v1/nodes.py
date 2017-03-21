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


class Nodes(Resource):

    def get(self):
        return utils.make_response(
            http_client.OK, nodes.Node.list_composed_nodes())

    def post(self):
        return utils.make_response(
            http_client.OK, nodes.Node.compose_node(request.get_json()))


class Node(Resource):

    def get(self, node_uuid):
        return utils.make_response(
            http_client.OK,
            nodes.Node.get_composed_node_by_uuid(node_uuid))

    def delete(self, node_uuid):
        return utils.make_response(
            http_client.OK, nodes.Node.delete_composed_node(node_uuid))


class NodeAction(Resource):

    def post(self, node_uuid):
        return utils.make_response(
            http_client.OK,
            nodes.Node.node_action(node_uuid, request.get_json()))


class NodesStorage(Resource):

    def get(self, nodeid):
        return abort(http_client.NOT_IMPLEMENTED)


class NodeRegister(Resource):

    def post(self, node_uuid):
        return utils.make_response(http_client.OK, nodes.Node.node_register(
                                   node_uuid))
