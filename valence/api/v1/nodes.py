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

from valence.redfish import redfish
from valence.validation import validator

LOG = logging.getLogger(__name__)


class NodesList(Resource):

    def get(self):
        return redfish.nodes_list(request.args)

    def post(self):
        return redfish.compose_node(request.get_json())


class Nodes(Resource):

    def get(self, nodeid):
        return redfish.get_nodebyid(nodeid)

    def delete(self, nodeid):
        return redfish.delete_composednode(nodeid)


class NodesStorage(Resource):

    def get(self, nodeid):
        return abort(501)
