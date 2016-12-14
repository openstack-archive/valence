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

"""Plugin for integrating Valence resources with Ironic bare metal services"""

from ironicclient import client

from valence import config as cfg
from valence.redfish import redfish


def _create_ironic_client(version=None):
    """Instantiate a new ironic client object."""
    params = {}
    if version is None:
        version = cfg.ironic_api_version
    params['os_username'] = cfg.ironic_username
    params['os_password'] = cfg.ironic_password
    params['os_auth_url'] = cfg.keystone_auth_url
    params['os_tenant_name'] = cfg.ironic_tenant_name
    if cfg.ironic_request_timeout is not None:
        params['timeout'] = cfg.ironic_request_timeout
    return client.get_client(str(version), **params)


class IronicClientWrapper(object):
    """Ironic client wrapper."""

    def __init__(self, version=None):
        self.client = _create_ironic_client(version)
        self.version = version


class IronicService(object):

    def __init__(self):
        self._client = IronicClientWrapper()
        self.redfish_url = cfg.url
        self.redfish_username = cfg.user
        self.redfish_password = cfg.password

    def enroll(self, system_id):
        system = redfish.get_systembyid(system_id)
        system_location = system['@odata.id']
        self._client.node.create(
            driver='redfish',
            driver_info={'redfish_address': self.redfish_url,
                         'redfish_username': self.redfish_username,
                         'redfish_password': self.redfish_password,
                         'redfish_system': system_location})
