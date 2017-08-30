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
from valence.podmanagers import manager
from valence.provision import driver
from valence.provision.ironic import utils

CONF = valence.conf.CONF

LOG = logging.getLogger(__name__)


class IronicDriver(driver.ProvisioningDriver):

    def __init__(self):
        super(IronicDriver, self).__init__()

    def node_register(self, node_uuid, param):
        LOG.debug('Registering node %s with ironic' % node_uuid)
        try:
            ironic = utils.create_ironicclient()
        except Exception as e:
            message = ('Error occurred while communicating to '
                       'Ironic: %s' % six.text_type(e))
            LOG.error(message)
            raise exception.ValenceException(message)
        try:
            n_info = nodes.Node(node_id=node_uuid).get_composed_node_by_uuid()
            podm_connection = manager.get_connection(n_info['podm_id'])
            n_args, p_args = podm_connection.get_ironic_node_params(n_info,
                                                                    **param)
            ironic_node = ironic.node.create(**n_args)
            p_args['node_uuid'] = ironic_node.uuid
            ironic.port.create(**p_args)
            db_api.Connection.update_composed_node(node_uuid,
                                                   {'managed_by': 'ironic'})
            return exception.confirmation(
                confirm_code="Node Registered",
                confirm_detail="The composed node {0} has been registered "
                               "with Ironic successfully.".format(node_uuid))
        except Exception as e:
            message = ('Unexpected error while registering node with '
                       'Ironic: %s' % six.text_type(e))
            LOG.error(message)
            raise exception.ValenceException(message)
