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
from oslo_middleware import request_id
from oslo_service import service
from pecan import configuration
from pecan import make_app
from valence.api import hooks
from valence.common import exceptions as p_excp

def setup_app(*args, **kwargs):
    config = {
        'server': {
            'host': cfg.CONF.api.bind_port,
            'port': cfg.CONF.api.bind_host
        },
        'app': {
            'root': 'valence.api.controllers.root.RootController',
            'modules': ['valence.api'],
            'errors': {
                400: '/error',
                '__force_dict__': True
            }
        }
    }
    pecan_config = configuration.conf_from_dict(config)

    app_hooks = [hooks.CORSHook()]

    app = make_app(
        pecan_config.app.root,
        hooks=app_hooks,
        force_canonical = False,
        logging=getattr(config, 'logging', {})
    )
    return app


_launcher = None


def serve(api_service, conf, workers=1):
    global _launcher
    if _launcher:
        raise RuntimeError('serve() can only be called once')

    _launcher = service.launch(conf, api_service, workers=workers)


def wait():
    _launcher.wait()
