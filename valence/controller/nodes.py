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
from valence.provision import driver
from valence.redfish import redfish

LOG = logging.getLogger(__name__)


class Node(object):

    @staticmethod
    def _show_node_brief_info(node_info):
        return {key: node_info[key] for key in node_info.keys()
                if key in ["uuid", "name", "index", "uri"]}

    @staticmethod
    def _create_compose_request(name, description, requirements):
        request = {}

        request["Name"] = name
        request["Description"] = description

        memory = {}
        if "memory" in requirements:
            if "capacity_mib" in requirements["memory"]:
                memory["CapacityMiB"] = requirements["memory"]["capacity_mib"]
            if "type" in requirements["memory"]:
                memory["DimmDeviceType"] = requirements["memory"]["type"]
        request["Memory"] = [memory]

        processor = {}
        if "processor" in requirements:
            if "model" in requirements["processor"]:
                processor["Model"] = requirements["processor"]["model"]
            if "total_cores" in requirements["processor"]:
                processor["TotalCores"] = (
                    requirements["processor"]["total_cores"])
        request["Processors"] = [processor]

        return request

    @classmethod
    def compose_node(cls, request_body):
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

        compose_request = cls._create_compose_request(name,
                                                      description,
                                                      requirements)

        # Call redfish to compose new node
        composed_node = redfish.compose_node(compose_request)

        composed_node["uuid"] = utils.generate_uuid()

        # Only store the minimum set of composed node info into backend db,
        # since other fields like power status may be changed and valence is
        # not aware.
        node_db = {"uuid": composed_node["uuid"],
                   "name": composed_node["name"],
                   "index": composed_node["index"],
                   "uri": composed_node["resource_uri"]}
        db_api.Connection.create_composed_node(node_db)

        return cls._show_node_brief_info(composed_node)

    @classmethod
    def manage_node(cls, request_body):
        """Manage existing RSD node.

        param request_body: Parameters for node to manage.

        Required JSON body:

        {
          'node_index': <Redfish index of node to manage>
        }

        return: Info on managed node.
        """
        composed_node = redfish.get_node_by_id(request_body["node_index"])
        # Check to see that the node to manage doesn't already exist in the
        # Valence database.
        error_msg = ("Node '%s' already managed by Valence")
        current_nodes = cls.list_composed_nodes()
        for node in current_nodes:
            if node['index'] == composed_node['index']:
                raise exception.ResourceExists(
                    error_msg % node['index'])

        composed_node["uuid"] = utils.generate_uuid()

        node_db = {"uuid": composed_node["uuid"],
                   "name": composed_node["name"],
                   "index": composed_node["index"],
                   "uri": composed_node["resource_uri"]}
        db_api.Connection.create_composed_node(node_db)

        return cls._show_node_brief_info(composed_node)

    @classmethod
    def get_composed_node_by_uuid(cls, node_uuid):
        """Get composed node details

        Get the detail of specific composed node. In some cases db data may be
        inconsistent with podm side, like user directly operate podm, not
        through valence api. So compare it with node info from redfish, and
        update db if it's inconsistent.

        param node_uuid: uuid of composed node
        return: detail of this composed node
        """

        node_db = db_api.Connection.get_composed_node_by_uuid(node_uuid)\
                        .as_dict()
        node_hw = redfish.get_node_by_id(node_db["index"])

        # Add those fields of composed node from db
        node_hw.update(node_db)

        return node_hw

    @classmethod
    def delete_composed_node(cls, node_uuid):
        """Delete a composed node

        param node_uuid: uuid of composed node
        return: message of this deletion
        """

        # Get node detail from db, and map node uuid to index
        index = db_api.Connection.get_composed_node_by_uuid(node_uuid).index

        # Call redfish to delete node, and delete corresponding entry in db
        message = redfish.delete_composed_node(index)
        db_api.Connection.delete_composed_node(node_uuid)

        return message

    @classmethod
    def list_composed_nodes(cls):
        """List all composed node

        return: brief info of all composed node
        """
        return [cls._show_node_brief_info(node_info.as_dict())
                for node_info in db_api.Connection.list_composed_nodes()]

    @classmethod
    def node_action(cls, node_uuid, request_body):
        """Post action to a composed node

        param node_uuid: uuid of composed node
        param request_body: parameter of node action
        return: message of this deletion
        """
        # Get node detail from db, and map node uuid to index
        index = db_api.Connection.get_composed_node_by_uuid(node_uuid).index
        return redfish.node_action(index, request_body)

    @classmethod
    def node_register(cls, node_uuid, request_body):
        """Register a node to  provisioning services.

        :param node_uuid: UUID of composed node to register
        :param request_body: parameter of register node with
        :returns: response from provisioning services
        """
        resp = driver.node_register(node_uuid, request_body)
        return resp
