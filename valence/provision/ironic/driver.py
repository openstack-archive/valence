# Copyright 2017 Intel.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

import six

from valence.common import exception
import valence.conf
from valence.controller import nodes
from valence.db import api as db_api
from valence.provision import driver
from valence.provision.ironic import utils

CONF = valence.conf.CONF

LOG = logging.getLogger(__name__)


class IronicDriver(driver.ProvisioningDriver):

    def __init__(self):
        super(IronicDriver, self).__init__()
        self.ironic = utils.create_ironicclient()

    def node_register(self, node_uuid, param):
        LOG.debug('Registering node %s with ironic' % node_uuid)
        node_controller = nodes.Node(node_id=node_uuid)
        try:
            node_info = node_controller.get_composed_node_by_uuid()
            node_args, port_args = (
                node_controller.connection.get_ironic_node_params(node_info,
                                                                  **param))
            ironic_node = self.ironic.node.create(**node_args)

        except Exception as e:
            message = ('Unexpected error while registering node with '
                       'Ironic: %s' % six.text_type(e))
            LOG.error(message)
            raise exception.ValenceException(message)

        node_info = db_api.Connection.update_composed_node(
            node_uuid, {'managed_by': 'ironic'}).as_dict()

        if port_args:
            # If MAC provided, create ports, else skip
            port_args['node_uuid'] = ironic_node.uuid
            self.ironic_port_create(**port_args)

        return node_info

    def ironic_port_create(self, **port):
        try:
            self.ironic.port.create(**port)
            LOG.debug('Successfully created ironic ports %s', port)
        except Exception as e:
            LOG.debug("Ironic port creation failed with error %s", str(e))
