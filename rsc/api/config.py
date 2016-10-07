#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from oslo_config import cfg
from oslo_log import log as logging
from rsc.common import rpc
import sys

LOG = logging.getLogger(__name__)

common_opts = [
    cfg.StrOpt('auth_strategy', default='noauth',
               help=("The type of authentication to use")),
    cfg.BoolOpt('allow_pagination', default=False,
                help=("Allow the usage of the pagination")),
    cfg.BoolOpt('allow_sorting', default=False,
                help=("Allow the usage of the sorting")),
    cfg.StrOpt('pagination_max_limit', default="-1",
               help=("The maximum number of items returned in a single "
                     "response, value was 'infinite' or negative integer "
                     "means no limit")),
]

api_opts = [
    cfg.StrOpt('bind_host', default='0.0.0.0',
               help=("The host IP to bind to")),
    cfg.IntOpt('bind_port', default=8181,
               help=("The port to bind to")),
    cfg.IntOpt('api_workers', default=2,
               help=("number of api workers"))
]


def init(args, **kwargs):
    # Register the configuration options
    api_conf_group = cfg.OptGroup(name='api', title='RSC API options')
    cfg.CONF.register_group(api_conf_group)
    cfg.CONF.register_opts(api_opts, group=api_conf_group)
    cfg.CONF.register_opts(common_opts)
    logging.register_options(cfg.CONF)

    cfg.CONF(args=args, project='rsc',
             **kwargs)

    rpc.init(cfg.CONF)


def setup_logging():
    """Sets up the logging options for a log with supplied name."""
    product_name = "rsc"
    logging.setup(cfg.CONF, product_name)
    LOG.info("Logging enabled!")
    LOG.debug("command line: %s", " ".join(sys.argv))


def list_opts():
    yield None, common_opts
