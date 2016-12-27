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
import os.path

from logging.handlers import RotatingFileHandler

from flask import Flask

from valence import config as cfg

_app = None


def setup_app():
    """Return Flask application"""
    app = Flask(cfg.PROJECT_NAME)
    app.url_map.strict_slashes = False
    TEN_KB = 10 * 1024

    # Configure logging
    if os.path.isfile(cfg.log_file) and os.access(cfg.log_file, os.W_OK):
        handler = RotatingFileHandler(
            cfg.log_file, maxBytes=TEN_KB, backupCount=1)
        handler.setLevel(cfg.log_level)
        formatter = logging.Formatter(cfg.log_format)
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
    app.logger.setLevel(cfg.log_level)
    return app


def get_app():
    global _app
    if not _app:
        _app = setup_app()
    return _app
