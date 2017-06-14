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
from valence.conductor.rpcapi import ComputeAPI as compute_api
import valence.conf
from verboselogs import VerboseLogger as getLogger

CONF = valence.conf.CONF
logging = getLogger(__name__)


class Node(object):

    @staticmethod
    def _show_node_brief_info(node_info):
        return {key: node_info[key] for key in six.iterkeys(node_info)
                if key in ["uuid", "name", "index", "links"]}

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
        return: compose node request status
        """
        task = compute_api.create_task('compose_node', request_body)
        logging.notice("\nvalence_api: Task created \n%s\n\n" % (task))
        req = {"topic": CONF.conductor.compute_topic,
               "method": "compose_node",
               "params": [request_body, task['uuid']]
               }

        compute_api.compose_node(req)
        res = {"stats": "compose request accepted and is queued"
               + " for processing",
               "task_uuid": task['uuid']}
        return res

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
        res = compute_api.manage_node(request_body)
        return res

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
        res = compute_api.get_composed_node_by_uuid(node_uuid)
        return res

    @classmethod
    def delete_composed_node(cls, node_uuid):
        """Delete a composed node

        param node_uuid: uuid of composed node
        return: message of this deletion
        """
        res = compute_api.delete_composed_node(node_uuid)
        return res

    @classmethod
    def list_composed_nodes(cls):
        """List all composed node

        return: brief info of all composed node
        """

        res = compute_api.list_composed_nodes()
        return res

    @classmethod
    def node_action(cls, node_uuid, request_body):
        """Post action to a composed node

        param node_uuid: uuid of composed node
        param request_body: parameter of node action
        return: message of this deletion
        """
        res = compute_api.node_action(node_uuid, request_body)
        return res

    @classmethod
    def node_register(cls, node_uuid, request_body):
        """Register a node to  provisioning services.

        :param node_uuid: UUID of composed node to register
        :param request_body: parameter of register node with
        :returns: response from provisioning services
        """
        res = compute_api.node_register(node_uuid, request_body)
        return res
