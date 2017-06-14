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

conductor_service_opts = [
    cfg.PortOpt('async_bind_port',
                default=5560,
                help=_('The port for the valence-conductor server.')),
    cfg.PortOpt('sync_bind_port',
                default=5561,
                help=_('The port for the valence-conductor server.')),
    cfg.IPOpt('bind_host',
              default='127.0.0.1',
              help=_('The listen IP for the valence-conductor server.')),
    cfg.StrOpt('compute_topic',
               default='compute',
               help=_('The topic on which valence-conductor service listens')),
    cfg.BoolOpt('debug',
                default=False,
                help=_('Enable debug mode for valence-conductor service.'))
]

log_option = [
    cfg.StrOpt('log_file',
               default='/var/log/valence/conductor/conductor.log',
               help=_('The log file location for valence-conductor service')),
    cfg.StrOpt('log_level',
               default='debug',
               help=_('The granularity of Error log outputs.')),
    cfg.StrOpt('log_format',
               default='%(asctime)s %(name)s %(filename)s:%(lineno)d'
                       + ' [%(levelname)s] %(message)s',
               help=_('The log format.')),
    cfg.DictOpt('field_styles',
                default={'asctime': {'color': ''}},
                help=_('The log field styles.')),
    cfg.DictOpt('level_styles',
                default={'notice': {'color': 'blue', 'bold': True},
                         'info': {'color': ""},
                         'error': {'color': 'red'},
                         'debug': {'color': 'green'},
                         'warning': {'color': 'yellow'},
                         'verbose': {'color': 'magenta'}},
                help=_('The log level styles.')),
]

conductor_group = cfg.OptGroup(name='conductor',
                               title='Options for the valence-conductor'
                               + ' service')


ALL_OPTS = (conductor_service_opts + log_option)


def register_opts(conf):
    conf.register_group(conductor_group)
    conf.register_opts(ALL_OPTS, conductor_group)


def list_opts():
    return {
        conductor_group: ALL_OPTS
    }
