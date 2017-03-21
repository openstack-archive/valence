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

from oslo_config import cfg

from valence.common.i18n import _


ironic_group = cfg.OptGroup(name='ironic_client',
                            title='Options for the Ironic client')

common_security_opts = [
    cfg.StrOpt('os_cacert',
               help=_('Optional CA cert file to use in SSL connections.')),
    cfg.StrOpt('os_cert',
               help=_('Optional PEM-formatted certificate chain file.')),
    cfg.StrOpt('os_key',
               help=_('Optional PEM-formatted file that contains the '
                      'private key.')),
    cfg.BoolOpt('insecure',
                default=False,
                help=_("If set, then the server's certificate will not "
                       "be verified."))]

ironic_client_opts = [
    cfg.StrOpt('username',
               help=_('The name of user to interact with Ironic API '
                      'service.')),
    cfg.StrOpt('password',
               help=_('Password of the user specified to authorize to '
                      'communicate with the Ironic API service.')),
    cfg.StrOpt('project',
               help=_('The project name which the user belongs to.')),
    cfg.StrOpt('auth_url',
               help=_('The OpenStack Identity Service endpoint to authorize '
                      'the user against.')),
    cfg.StrOpt('user_domain_id',
               help=_(
                   'ID of a domain the user belongs to.')),
    cfg.StrOpt('project_domain_id',
               help=_(
                   'ID of a domain the project belongs to.')),
    cfg.StrOpt('api_version',
               default='1',
               help=_('Version of Ironic API to use in ironicclient.'))]


ALL_OPTS = (ironic_client_opts + common_security_opts)


def register_opts(conf):
    conf.register_group(ironic_group)
    conf.register_opts(ALL_OPTS, group=ironic_group)


def list_opts():
    return {ironic_group: ALL_OPTS}
