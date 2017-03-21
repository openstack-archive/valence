# Copyright 2017 Intel.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from ironicclient import client as ironicclient

from valence.common import exception
import valence.conf

CONF = valence.conf.CONF


class OpenStackClients(object):
    """Convenience class to create and cache client instances."""

    def __init__(self, context=None):
        self.context = context
        self._ironic = None

    def _get_client_option(self, client, option):
        return getattr(getattr(valence.conf.CONF, '%s_client' % client),
                       option)

    @exception.wrap_keystone_exception
    def ironic(self):
        if self._ironic:
            return self._ironic

        ironicclient_version = self._get_client_option('ironic', 'api_version')
        args = {
            'os_auth_url': self._get_client_option('ironic', 'auth_url'),
            'os_username': self._get_client_option('ironic', 'username'),
            'os_password': self._get_client_option('ironic', 'password'),
            'os_project_name': self._get_client_option('ironic', 'project'),
            'os_project_domain_id': self._get_client_option(
                'ironic', 'project_domain_id'),
            'os_user_domain_id': self._get_client_option(
                'ironic', 'user_domain_id'),
            'os_cacert': self._get_client_option('ironic', 'os_cacert'),
            'os_cert': self._get_client_option('ironic', 'os_cert'),
            'os_key': self._get_client_option('ironic', 'os_key'),
            'insecure': self._get_client_option('ironic', 'insecure')
        }
        self._ironic = ironicclient.get_client(ironicclient_version, **args)

        return self._ironic
