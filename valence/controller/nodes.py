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

from valence.common import exception
from valence.common import utils
from valence.controller import flavors
from valence.db import api as db_api
from valence.podmanagers import manager
from valence.provision import driver

LOG = logging.getLogger(__name__)


class Node(object):

    def __init__(self, node_id=None, podm_id=None):
        """Create node object

        node uuid or podmanager uuid is required to create the
        podmanager connection object.

        :param node_id Node uuid
        :param podm_id podmanager id

        """
        self.podm_id = podm_id
        if node_id:
            self.node = db_api.Connection.get_composed_node_by_uuid(node_id).\
                as_dict()
            self.podm_id = self.node['podm_id']

        self.connection = manager.get_connection(self.podm_id)

    @staticmethod
    def _show_node_brief_info(node_info):
        return {key: node_info[key] for key in node_info.keys()
                if key in ["uuid", "name", "podm_id", "index", "resource_uri"]}

    def compose_node(self, request_body):
        """Compose new node

        param request_body: parameter for node composition
        return: brief info of this new composed node
        """

        if "flavor_id" in request_body:
            flavor = flavors.get_flavor(request_body["flavor_id"])
            requirements = flavor["properties"]
        elif "properties" in request_body:
            requirements = request_body["properties"]
        else:
            requirements = {
                "memory": {},
                "processor": {}
            }

        name = request_body["name"]
        # "description" is optional
        description = request_body.get("description", "")

        # Moving _create_compose_request to drivers as this can be
        # vendor specific request
        composed_node = self.connection.compose_node(name, description,
                                                     requirements)
        composed_node["uuid"] = utils.generate_uuid()

        # Only store the minimum set of composed node info into backend db,
        # since other fields like power status may be changed and valence is
        # not aware.
        node_db = {"uuid": composed_node["uuid"],
                   "podm_id": self.podm_id,
                   "name": composed_node["name"],
                   "index": composed_node["index"],
                   "resource_uri": composed_node["resource_uri"]}
        db_api.Connection.create_composed_node(node_db)

        return self._show_node_brief_info(composed_node)

    def manage_node(self, request_body):
        """Manage existing RSD node.

        param request_body: Parameters for node to manage.

        Required JSON body:

        {'node_index': <Redfish index of node to manage>,
         'podm_id': <podmanager id with which node is managed>}

        return: Info on managed node.
        """
        # Check to see that the node to manage doesn't already exist in the
        # Valence database.
        node_index = request_body["node_index"]
        error_msg = ("Node '%s' already managed by Valence")
        current_nodes = self.list_composed_nodes()
        for node in current_nodes:
            if node['index'] == node_index:
                raise exception.ResourceExists(error_msg % node_index)

        # Get podm connection with which node should be managed
        composed_node = self.connection.get_node_info(node_index)
        composed_node["uuid"] = utils.generate_uuid()

        node_db = {"uuid": composed_node["uuid"],
                   "name": composed_node["name"],
                   "podm_id": self.podm_id,
                   "index": composed_node["index"],
                   "resource_uri": composed_node["resource_uri"]}
        db_api.Connection.create_composed_node(node_db)

        return self._show_node_brief_info(composed_node)

    def get_composed_node_by_uuid(self):
        """Get composed node details

        Get the detail of specific composed node. In some cases db data may be
        inconsistent with podm side, like user directly operate podm, not
        through valence api. So compare it with node info from redfish, and
        update db if it's inconsistent.

        return: detail of this composed node
        """

        # Get podm connection to retrieve details
        node_hw = self.connection.get_node_info(self.node['index'])
        # Add those fields of composed node from db
        node_hw.update(self.node)
        return node_hw

    def delete_composed_node(self):
        """Delete a composed node

        return: message of this deletion
        """
        # Call podmanager to delete node, and delete corresponding entry in db
        message = self.connection.delete_composed_node(self.node['index'])
        db_api.Connection.delete_composed_node(self.node['uuid'])

        return message

    @classmethod
    def list_composed_nodes(cls, filters={}):
        """List all composed node

        return: brief info of all composed node
        """
        return [cls._show_node_brief_info(node.as_dict())
                for node in db_api.Connection.list_composed_nodes(filters)]

    def node_action(self, request_body):
        """Post action to a composed node

        param node_uuid: uuid of composed node
        param request_body: parameter of node action
        return: message of this deletion
        """
        node_index = self.node['index']
        return self.connection.node_action(node_index, request_body)

    @classmethod
    def node_register(cls, node_uuid, request_body):
        """Register a node to  provisioning services.

        :param node_uuid: UUID of composed node to register
        :param request_body: parameter of register node with
        :returns: response from provisioning services
        """
        resp = driver.node_register(node_uuid, request_body)
        return resp
