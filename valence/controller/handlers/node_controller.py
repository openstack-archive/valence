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

import json
from oslo_log import log as logging
from valence.common import osinterface as osapi
from valence.common.redfish import api as rfsapi
import requests

LOG = logging.getLogger(__name__)


class Handler(object):
    """Valence Node RPC handler.

    These are the backend operations. They are executed by the backend ervice.
    API calls via AMQP (within the ReST API) trigger the handlers to be called.

    """

    def __init__(self):
        super(Handler, self).__init__()

    def list_nodes(self, context, filters):
        LOG.info(str(filters))
        return rfsapi.nodes_list(None, filters)

    def get_nodebyid(self, context, nodeid):
        return rfsapi.get_nodebyid(nodeid)

    def delete_composednode(self, context, nodeid):
        return rfsapi.delete_composednode(nodeid)

    def update_node(self, context, nodeid):
        return {"node": "Update node attributes"}

    def compose_nodes(self, context, criteria):
        """Chassis details could also be fetched and inserted"""

        # no of nodes to compose
        nodes_to_compose = int(criteria["nodes"]) if "nodes" in criteria else 1
        node_criteria = criteria["filter"] if "filter" in criteria else {}
        #no of node is not currently implemented
        return rfsapi.compose_node(node_criteria)

    def list_node_storages(self, context, data):
        return {"node": "List the storages attached to the node"}

    def map_node_storage(self, context, data):
        return {"node": "Map storages to a node"}

    def delete_node_storage(self, context, data):
        return {"node": "Deleted storages mapped to a node"}
