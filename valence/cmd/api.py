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

import gunicorn.app.base
from gunicorn.six import iteritems

from valence.api.route import app as application
from valence import config as cfg


LOG = logging.getLogger(__name__)


class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def main():
    options = {
        'bind': '%s:%s' % (cfg.bind_host, cfg.bind_port),
        'reload': cfg.debug,
        'timeout': cfg.timeout,
        'workers': cfg.workers
    }
    LOG.info(("Valence Server on http://%(host)s:%(port)s"),
             {'host': cfg.bind_host, 'port': cfg.bind_port})
    StandaloneApplication(application, options).run()


if __name__ == '__main__':
    main()
