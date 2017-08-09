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


log_opts = [
    cfg.StrOpt('log_file',
               default='/var/log/valence/valence.log',
               help=_('The log file location for valence service')),
    cfg.StrOpt('log_level',
               default='info',
               choices=['info', 'critical', 'warning', 'debug', 'error',
                        'notset'],
               help=_('The granularity of log outputs. By default set to '
                      'info level')),
    cfg.StrOpt('log_format',
               default='%(asctime)s %(name)-4s %(levelname)-4s %(message)s',
               help=_('The log format.')),
]

ALL_OPTS = (log_opts)


def register_opts(conf):
    conf.register_opts(ALL_OPTS)


def list_opts():
    return {
        'DEFAULT': ALL_OPTS
    }
