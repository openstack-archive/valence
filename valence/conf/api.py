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

api_service_opts = [
    cfg.PortOpt('bind_port',
                default=8181,
                help=_('The port for the valence API server.')),
    cfg.IPOpt('bind_host',
              default='127.0.0.1',
              help=_('The listen IP for the valence API server.')),
    cfg.BoolOpt('enable_ssl_api',
                default=False,
                help=_("Enable the integrated stand-alone API to service "
                       "requests via HTTPS instead of HTTP. If there is a "
                       "front-end service performing HTTPS offloading from "
                       "the service, this option should be False; note, you "
                       "will want to change public API endpoint to represent "
                       "SSL termination URL with 'public_endpoint' option.")),
    cfg.IntOpt('workers',
               default=4,
               help=_('Number of workers for valence-api service. '
                      'The default will be the number of CPUs available.')),
    cfg.IntOpt('timeout',
               default=1000,
               help=_('The maximum timeout to wait for valence API server '
                      'to come up.')),
    cfg.IntOpt('max_limit',
               default=1000,
               help=_('The maximum number of items returned in a single '
                      'response from a collection resource.')),
    cfg.StrOpt('api_paste_config',
               default='api-paste.ini',
               help=_('Configuration file for WSGI definition of API.')),
    cfg.BoolOpt('debug',
                default=False,
                help=_('Start API server in debug mode.'))
]

log_option = [
    cfg.StrOpt('log_file',
               default='/var/log/valence/valence-api.log',
               help=_('The log file location for valence API server')),
    cfg.StrOpt('log_level',
               default='info',
               choices=['info', 'critical', 'warning', 'debug', 'error'],
               help=_('The granularity of API server log outputs.')),
]

api_group = cfg.OptGroup(name='api',
                         title='Options for the valence API ')


ALL_OPTS = (api_service_opts + log_option)


def register_opts(conf):
    conf.register_group(api_group)
    conf.register_opts(ALL_OPTS, api_group)


def list_opts():
    return {
        api_group: ALL_OPTS
    }
