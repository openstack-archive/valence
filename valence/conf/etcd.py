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

etcd_service_opts = [
    cfg.PortOpt('port',
                default=2379,
                help=_('The port for the etcd server.')),
    cfg.IPOpt('host',
              default='127.0.0.1',
              help=_('The listen IP for the etcd server.')),
]

etcd_group = cfg.OptGroup(name='etcd',
                          title='Options for the etcd service')


ALL_OPTS = (etcd_service_opts)


def register_opts(conf):
    conf.register_group(etcd_group)
    conf.register_opts(ALL_OPTS, etcd_group)


def list_opts():
    return {
        etcd_group: ALL_OPTS
    }
