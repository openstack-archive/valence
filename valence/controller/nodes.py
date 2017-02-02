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

import six

from valence.common import utils
from valence.db import api as db_api
from valence.redfish import redfish


class Node(object):

    @staticmethod
    def _show_node_brief_info(node_info):
        return {key: node_info[key] for key in six.iterkeys(node_info)
                if key in ["uuid", "name", "links"]}

    @classmethod
    def compose_node(cls, request_body):
        """Compose new node

        param request_body: parameter for node composition
        return: brief info of this new composed node
        """

        # Call redfish to compose new node
        composed_node = redfish.compose_node(request_body)

        composed_node["uuid"] = utils.generate_uuid()

        # Only store the minimum set of composed node info into backend db,
        # since other fields like power status may be changed and valence is
        # not aware.
        node_db = {"uuid": composed_node["uuid"],
                   "name": composed_node["name"],
                   "index": composed_node["index"],
                   "links": composed_node["links"]}
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

        # TODO(lin.yang): should validate request body whether follow specifc
        # format, like
        #     {
        #       "Reset": {
        #         "Type": "On"
        #     }
        # }
        # This should be covered on commit
        # https://review.openstack.org/#/c/422547/

        return redfish.node_action(index, request_body)
