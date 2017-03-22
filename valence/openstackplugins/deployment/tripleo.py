# Copyright (c) 2017 Intel, Inc.
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
import logging

from valence import config as cfg

LOG = logging.getLogger(__name__)


class TripleO(object):

    @staticmethod
    def _create_instack_node(node):
        instack_node = {}
        node_metadata = node["metadata"]
        #TODO(ntpttr) We can get driver information from node metadata when
        #     multiple drivers are supported. 
        instack_node["pm_type"] = "redfish"
        instack_node["mac"] = [node_metadata["network"][0]["mac"]]
        instack_node["cpu"] = node_metadata["processor"][0]["total_core"]
        instack_node["memory"] = node_metadata["memory"][0]["total_memory_mb"]
        #TODO(ntpttr) add disk when that information is being saved in node info
        instack_node["arch"] = node_metadata["processor"][0]["instruction_set"]
        instack_node["pm_user"] = cfg.podm_user
        instack_node["pm_password"] = cfg.podm_password
        instack_node["pm_addr"] = cfg.podm_url
        return instack_node

    @classmethod
    def write_instack_file(cls, deploy_nodes):
        instack_env = {"nodes": []}
        for node in deploy_nodes:
            instack_node = cls._create_instack_node(node)
            instack_env["nodes"].append(instack_node)
        
        try:
            with open("/tmp/instackenv.json", "w") as f:
                f.write(json.dumps(instack_env, indent=4, sort_keys=True))
        except IOError:
            LOG.error("Failed to write inistackenv.json")