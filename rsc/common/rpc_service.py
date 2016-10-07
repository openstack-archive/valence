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

"""Common RPC service and API tools for RSC."""

import eventlet
from oslo_config import cfg
import oslo_messaging as messaging
from oslo_service import service

from rsc.common import rpc
from rsc.objects import base as objects_base

eventlet.monkey_patch()

periodic_opts = [
    cfg.IntOpt('periodic_interval_max',
               default=60,
               help='Max interval size between periodic tasks execution in '
                    'seconds.'),
]

CONF = cfg.CONF
CONF.register_opts(periodic_opts)


class Service(service.Service):

    def __init__(self, topic, server, handlers, binary):
        super(Service, self).__init__()
        serializer = rpc.RequestContextSerializer(
            objects_base.RSCObjectSerializer())
        transport = messaging.get_transport(cfg.CONF)
        # TODO(asalkeld) add support for version='x.y'
        target = messaging.Target(topic=topic, server=server)
        self._server = messaging.get_rpc_server(transport, target, handlers,
                                                serializer=serializer)
        self.binary = binary

    def start(self):
        # servicegroup.setup(CONF, self.binary, self.tg)
        self._server.start()

    def stop(self):
        if self._server:
            self._server.stop()
            self._server.wait()
        super(Service, self).stop()

    @classmethod
    def create(cls, topic, server, handlers, binary):
        service_obj = cls(topic, server, handlers, binary)
        return service_obj


class API(object):
    def __init__(self, transport=None, context=None, topic=None, server=None,
                 timeout=None):
        serializer = rpc.RequestContextSerializer(
            objects_base.RSCObjectSerializer())
        if transport is None:
            exmods = rpc.get_allowed_exmods()
            transport = messaging.get_transport(cfg.CONF,
                                                allowed_remote_exmods=exmods)
        self._context = context
        if topic is None:
            topic = ''
        target = messaging.Target(topic=topic, server=server)
        self._client = messaging.RPCClient(transport, target,
                                           serializer=serializer,
                                           timeout=timeout)

    def _call(self, method, *args, **kwargs):
        return self._client.call(self._context, method, *args, **kwargs)

    def _cast(self, method, *args, **kwargs):
        self._client.cast(self._context, method, *args, **kwargs)

    def echo(self, message):
        self._cast('echo', message=message)
