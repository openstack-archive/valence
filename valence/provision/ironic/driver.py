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

import requests
import six

from valence.common import exception
import valence.conf
from valence.controller import nodes
from valence.db import api as db_api
from valence.provision import driver
from valence.provision.ironic import utils
from valence.redfish import redfish

CONF = valence.conf.CONF

LOG = logging.getLogger(__name__)


class IronicDriver(driver.ProvisioningDriver):

    def __init__(self):
        super(IronicDriver, self).__init__()

    def node_register(self, node_uuid, param):
        LOG.debug('Registering node %s with ironic' % node_uuid)
        try:
            node_info = nodes.Node.get_composed_node_by_uuid(node_uuid)
        except exception.NotFound:
            raise
        try:
            ironic = utils.create_ironicclient()
        except Exception as e:
            message = ('Error occurred while communicating to '
                       'Ironic: %s' % six.text_type(e))
            LOG.error(message)
            raise exception.ValenceException(message)
        try:
            system = redfish.systems_list()
        except Exception as e:
            message = ('Error occurred while communicating to '
                       'Redfish API: %s' % six.text_type(e))
            LOG.error(message)
            raise exception.ValenceException(message)
        try:
            driver_info = {
                'redfish_root_uri': requests.compat.urljoin(
                    CONF.podm.url, CONF.podm.base_ext),
                'redfish_username': CONF.podm.username,
                'redfish_password': CONF.podm.password,
                'redfish_verify_ca': CONF.podm.verify_ca,
                'redfish_system_id': system[0]['id']}
            node_args = {}
            if param:
                if param.get('driver_info', None):
                    driver_info.update(param.get('driver_info'))
                    del param['driver_info']
            node_args.update({'driver': 'redfish', 'name': node_info['name'],
                              'driver_info': driver_info})
            if param:
                node_args.update(param)
            ironic_node = ironic.node.create(**node_args)
            port_args = {'node_uuid': ironic_node.uuid,
                         'address': node_info['metadata']['network'][0]['mac']}
            ironic.port.create(**port_args)
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
            raise exception.ValenceException(message, e.http_status)
