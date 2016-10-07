# Copyright (c) 2016 Intel, Inc.
#
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

"""Config options for RSC controller Service"""

from oslo_config import cfg
from oslo_log import log as logging
import sys

LOG = logging.getLogger(__name__)

CONTROLLER_OPTS = [
    cfg.StrOpt('topic',
               default='rsc-controller',
               help='The queue to add controller tasks to.')
]

OS_INTERFACE_OPTS = [
    cfg.StrOpt('os_admin_url',
               help='Admin URL of Openstack'),
    cfg.StrOpt('os_tenant',
               default='admin',
               help='Tenant for Openstack'),
    cfg.StrOpt('os_user',
               default='admin',
               help='User for openstack'),
    cfg.StrOpt('os_password',
               default='addmin',
               help='Password for openstack')
]

controller_conf_group = cfg.OptGroup(name='controller',
                                     title='RSC controller options')
cfg.CONF.register_group(controller_conf_group)
cfg.CONF.register_opts(CONTROLLER_OPTS, group=controller_conf_group)

os_conf_group = cfg.OptGroup(name='undercloud',
                             title='RSC Openstack interface options')
cfg.CONF.register_group(os_conf_group)
cfg.CONF.register_opts(OS_INTERFACE_OPTS, group=os_conf_group)


def init(args, **kwargs):
    # Register the configuration options
    logging.register_options(cfg.CONF)
    cfg.CONF(args=args, project='rsc', **kwargs)


def setup_logging():
    """Sets up the logging options for a log with supplied name."""
    domain = "rsc"
    logging.setup(cfg.CONF, domain)
    LOG.info("Logging enabled!")
    LOG.debug("command line: %s", " ".join(sys.argv))
