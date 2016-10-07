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

"""controller API for interfacing with Other modules"""
from oslo_config import cfg
from oslo_log import log as logging
from rsc.common import rpc_service


# The Backend API class serves as a AMQP client for communicating
# on a topic exchange specific to the controllers.  This allows the ReST
# API to trigger operations on the controllers

LOG = logging.getLogger(__name__)


class API(rpc_service.API):
    def __init__(self, transport=None, context=None, topic=None):
        if topic is None:
            cfg.CONF.import_opt('topic', 'rsc.controller.config',
                                group='controller')
        super(API, self).__init__(transport, context,
                                  topic=cfg.CONF.controller.topic)

    # Flavor Operations

    def flavor_options(self):
        return self._call('flavor_options')

    def flavor_generate(self, criteria):
        return self._call('flavor_generate', criteria=criteria)

    # Node(s) Operations
    def list_nodes(self, filters):
        return self._call('list_nodes', filters=filters)

    def get_nodebyid(self, nodeid):
        return self._call('get_nodebyid', nodeid=nodeid)

    def delete_composednode(self, nodeid):
        return self._call('delete_composednode', nodeid=nodeid)

    def update_node(self, nodeid):
        return self._call('update_node')

    def compose_nodes(self, criteria):
        return self._call('compose_nodes', criteria=criteria)

    def list_node_storages(self, data):
        return self._call('list_node_storages')

    def map_node_storage(self, data):
        return self._call('map_node_storage')

    def delete_node_storage(self, data):
        return self._call('delete_node_storage')
