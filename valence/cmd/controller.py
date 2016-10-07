#!/usr/bin/env python

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

"""Starter script for the Valence controller service."""

import os
from oslo_config import cfg
from oslo_log import log as logging
from oslo_service import service
from valence.common import rpc_service
from valence.controller import config as controller_config
from valence.controller.handlers import flavor_controller
from valence.controller.handlers import node_controller
# from valence import version
import sys
import uuid

LOG = logging.getLogger(__name__)


def main():
    controller_config.init(sys.argv[1:])
    controller_config.setup_logging()
    LOG.info(('Starting valence-controller in PID %s'), os.getpid())
    LOG.debug("Configuration:")
#   cfg.CONF.import_opt('topic',
#                       'valence.controller.config',
#                        group='controller')

    controller_id = uuid.uuid4()
    endpoints = [
        flavor_controller.Handler(),
        node_controller.Handler()
    ]

    server = rpc_service.Service.create(cfg.CONF.controller.topic,
                                        controller_id, endpoints,
                                        binary='valence-controller')
    launcher = service.launch(cfg.CONF, server)
    launcher.wait()

if __name__ == '__main__':
    main()
