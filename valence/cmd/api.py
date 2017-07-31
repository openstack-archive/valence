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

import logging

import eventlet
eventlet.monkey_patch(os=False)
import gunicorn.app.base

from valence.api.route import app as application
import valence.conf
from valence.controller import pooled_devices

CONF = valence.conf.CONF
LOG = logging.getLogger(__name__)


class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in self.options.items()
                       if key in self.cfg.settings and value is not None])
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def sync_devices(server):
    pooled_devices.PooledDevices.start_devices_periodic_task()


def main():
    options = {
        'bind': '%s:%s' % (CONF.api.bind_host, CONF.api.bind_port),
        'reload': CONF.api.debug,
        'timeout': CONF.api.timeout,
        'workers': CONF.api.workers,
        'loglevel': CONF.api.log_level,
        'errorlog': CONF.api.log_file,
        'worker_class': 'eventlet',
        'when_ready': sync_devices,
    }
    LOG.info(("Valence Server on http://%(host)s:%(port)s"),
             {'host': CONF.api.bind_host, 'port': CONF.api.bind_port})
    StandaloneApplication(application, options).run()


if __name__ == '__main__':
    main()
