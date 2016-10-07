#!/usr/bin/env python

# copyright (c) 2016 Intel, Inc.
#
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

import sys

from oslo_config import cfg
from oslo_log import log as logging
from oslo_service import wsgi

from valence.api import app
from valence.api import config as api_config

CONF = cfg.CONF
LOG = logging.getLogger('valence.api')


def main():
    api_config.init(sys.argv[1:])
    api_config.setup_logging()
    application = app.setup_app()
    host = CONF.api.bind_host
    port = CONF.api.bind_port
    workers = 1

    LOG.info(("Server on http://%(host)s:%(port)s with %(workers)s"),
             {'host': host, 'port': port, 'workers': workers})

    service = wsgi.Server(CONF, "valence", application, host, port)

    app.serve(service, CONF, workers)

    LOG.info("Configuration:")
    app.wait()


if __name__ == '__main__':
    main()
