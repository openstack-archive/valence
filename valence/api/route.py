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

from flask_cors import CORS
from flask_restful import Api
from six.moves import http_client

from valence.api import app as flaskapp
from valence.api.root import PODMProxy
from valence.api.root import Root
from valence.api.v1.flavors import Flavors as v1Flavors
from valence.api.v1.nodes import Nodes as v1Nodes
from valence.api.v1.nodes import NodesList as v1NodesList
from valence.api.v1.nodes import NodesStorage as v1NodesStorage
from valence.api.v1.storages import Storages as v1Storages
from valence.api.v1.storages import StoragesList as v1StoragesList
from valence.api.v1.systems import Systems as v1Systems
from valence.api.v1.systems import SystemsList as v1SystemsList
from valence.api.v1.version import V1
from valence.common import exception
from valence import config as cfg


app = flaskapp.get_app()
cors = CORS(app)


class ValenceService(Api):
    """Overriding Flask Restful Error handler"""

    def handle_error(self, error):

        if cfg.debug == 'false':
            if issubclass(error.__class__, exception.ValenceError):
                return self.make_response(error.as_dict(), error.status)
            elif hasattr(error, 'status'):
                return self.make_response(exception.httpexception(error),
                                          error.code)
            else:
                return self.make_response(
                    exception.generalexception(
                        error, http_client.INTERNAL_SERVER_ERROR),
                    http_client.INTERNAL_SERVER_ERROR)
        else:
            super(ValenceService, self).handle_error(self)


api = ValenceService(app)

"""API V1.0 Operations"""


# API Root operation
api.add_resource(Root, '/', endpoint='root')

# V1 Root operations
api.add_resource(V1, '/v1', endpoint='v1')

# Node(s) operations
api.add_resource(v1NodesList, '/v1/nodes', endpoint='nodes')
api.add_resource(v1Nodes, '/v1/nodes/<string:nodeid>', endpoint='node')
api.add_resource(v1NodesStorage,
                 '/v1/nodes/<string:nodeid>/storages',
                 endpoint='nodes_storages')

# System(s) operations
api.add_resource(v1SystemsList, '/v1/systems', endpoint='systems')
api.add_resource(v1Systems, '/v1/systems/<string:systemid>', endpoint='system')

# Flavor(s) operations
api.add_resource(v1Flavors, '/v1/flavors', endpoint='flavors')


# Storage(s) operations
api.add_resource(v1StoragesList, '/v1/storages', endpoint='storages')
api.add_resource(v1Storages,
                 '/v1/storages/<string:storageid>', endpoint='storage')

# Proxy to PODM
api.add_resource(PODMProxy, '/<path:url>', endpoint='podmproxy')
