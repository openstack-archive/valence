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

openstack_opts = [
    cfg.StrOpt('auth_url',
               help=_('The auth URL of openstack cloud. (e.g.: '
                      'http(s)://<IP>:<PORT>/<identity service api version>')),
    cfg.StrOpt('username',
               help=_('Openstack User name with admin privilege')),
    cfg.StrOpt('password',
               help=_('Openstack User account password')),
    cfg.StrOpt('project_name',
               help=_('Openstack project name')),
    cfg.StrOpt('user_domain_id',
               help=_('Openstack users domain id ')),
    cfg.StrOpt('project_domain_id',
               help=_('Openstack projects domain id ')),
    cfg.StrOpt('nova_api_version',
               help=_('nova api version ')),

]


openstack_group = cfg.OptGroup(name='openstack',
                               title='openstack credentials')


ALL_OPTS = (openstack_opts)


def register_opts(conf):
    conf.register_group(openstack_group)
    conf.register_opts(ALL_OPTS, openstack_group)


def list_opts():
    return {
        openstack_group: ALL_OPTS
    }
