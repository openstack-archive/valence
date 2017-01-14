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
from six.moves import http_client

from valence.common import utils
from valence.db import api as db_api
from valence.redfish import redfish

LOG = logging.getLogger(__name__)


class NodesList(Resource):

    def get(self):
        return redfish.nodes_list(request.args)

    def post(self):
        # Call redfish to compose new node
        composed_node = redfish.compose_node(request.get_json())

        # Store new composed node info into backend db
        db_api.Connection.create_composed_node(composed_node)

        return utils.make_response(
            http_client.OK, composed_node)


class Nodes(Resource):

    def get(self, node_uuid):
        """Get composed node details

        Get the detail of specific composed node from backend db. In some cases
        db data may be inconsistent with podm side, like user directly operate
        podm, not through valence api.

        param node_uuid: uuid of composed node
        return: detail of this composed node
        """

        return utils.make_response(
            http_client.OK,
            db_api.Connection.get_composed_node_by_uuid(node_uuid).as_dict())

    def delete(self, node_uuid):
        # Get node detail from db, and map node uuid to index
        index = db_api.Connection.get_composed_node_by_uuid(node_uuid).index

        # Call redfish to delete node, and delete corresponding entry in db
        message = redfish.delete_composednode(index)
        db_api.Connection.get_composed_node_by_uuid(node_uuid)

        return utils.make_response(http_client.OK, message)


class NodesStorage(Resource):

    def get(self, nodeid):
        return abort(501)
