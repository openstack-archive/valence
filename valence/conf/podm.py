# Copyright (c) 2017 Intel, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the 'License');
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an 'AS IS' BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from oslo_config import cfg

from valence.common.i18n import _

podm_opts = [
    cfg.StrOpt('url',
               help=_('The URL of Redfish API server. (e.g.: '
                      'http(s)://<IP>:<PORT>/). Required.')),
    cfg.StrOpt('username',
               help=_('User account with admin/server-profile access '
                      'privilege. Although this property is not '
                      'mandatory it\'s highly recommended to set a '
                      'username. Optional.')),
    cfg.StrOpt('password',
               help=_('User account password. Although this property is '
                      'not mandatory, it\'s highly recommended to set a '
                      'password. Optional.')),
    cfg.BoolOpt('verify_ca',
                help=_('Either a boolean value, a path to a CA_BUNDLE '
                       'file or directory with certificates of trusted '
                       'CAs. If set to True the driver will verify the '
                       'host certificates; if False the driver will '
                       'ignore verifying the SSL certificate; If it\'s '
                       'a path the driver will use the specified '
                       'certificate or one of the certificates in the '
                       'directory. Defaults to True. Optional.')),
    cfg.StrOpt('base_ext',
               default='/redfish/v1/',
               help=_('The URL extension that specifies the '
                      'Redfish API version that valence will interact with')),
    cfg.BoolOpt('enable_periodic_sync',
                default=False,
                help=_('To enable periodic task to automatically sync '
                       'resources of podmanager with DB.')),
    cfg.IntOpt('sync_interval',
               default=30,
               help=_('Time interval(in seconds) after which devices will be '
                      'synced periodically.')),
]


podm_group = cfg.OptGroup(name='podm',
                          title='Options for the Refish API service')


ALL_OPTS = (podm_opts)


def register_opts(conf):
    conf.register_group(podm_group)
    conf.register_opts(ALL_OPTS, podm_group)


def list_opts():
    return {
        podm_group: ALL_OPTS
    }
