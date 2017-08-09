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

import logging
import logging.handlers
import os.path


import flask

from valence.common import config
import valence.conf

CONF = valence.conf.CONF
PROJECT_NAME = 'valence'
_app = None

log_level_map = {'debug': logging.DEBUG,
                 'info': logging.INFO,
                 'warning': logging.WARNING,
                 'error': logging.ERROR,
                 'critical': logging.CRITICAL,
                 'notset': logging.NOTSET}


def setup_app():
    """Return Flask application"""
    config.parse_args(prog=PROJECT_NAME)
    app = flask.Flask(PROJECT_NAME)
    app.url_map.strict_slashes = False
    TEN_KB = 10 * 1024

    # Configure logging
    if os.path.isfile(CONF.log_file) and os.access(CONF.log_file, os.W_OK):
        handler = logging.handlers.RotatingFileHandler(
            CONF.api.log_file, maxBytes=TEN_KB, backupCount=1)
        handler.setLevel(log_level_map.get(CONF.log_level))
        formatter = logging.Formatter(CONF.log_format)
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
    app.logger.setLevel(log_level_map.get(CONF.log_level))

    @app.before_request
    def before_request_logging():
        req = flask.request
        app.logger.debug('{0} {1}'.format(req.method, req.url))
        app.logger.debug('Request Headers: {0}'.format(dict(req.headers)))
        if req.data:
            app.logger.debug('Request Content: {0}'.format(req.data))

    @app.after_request
    def after_request_logging(resp):
        app.logger.debug('Response Headers: {0}'.format(dict(resp.headers)))
        if resp.data:
            app.logger.debug('Response Content: {0}'.format(resp.data))
        return resp

    return app


def get_app():
    global _app
    if not _app:
        _app = setup_app()
    return _app
