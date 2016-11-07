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
from valence.api import app as flaskapp
from valence.api.root import PODMProxy
from valence.api.root import Root
from valence.api.v1.flavor import Flavors as v1Flavors
from valence.api.v1.nodes import Nodes as v1Nodes
from valence.api.v1.nodes import NodesList as v1NodesList
from valence.api.v1.nodes import NodesStorage as v1NodesStorage
from valence.api.v1.resources import PooledResources as v1Resources
from valence.api.v1.resources import PooledResourcesList as v1ResourcesList
from valence.api.v1.systems import Systems as v1Systems
from valence.api.v1.systems import SystemsList as v1SystemsList
from valence.api.v1.version import V1

app = flaskapp.get_app()
cors = CORS(app)
api = Api(app)

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
api.add_resource(v1Flavors, '/v1/flavor', endpoint='flavor')


# Storage(s) operations
api.add_resource(v1ResourcesList, '/v1/resources', endpoint='pooledresources')
api.add_resource(v1Resources,
                 '/v1/resources/<string:resourcesid>',
                 endpoint='pooledresource')

# Proxy to PODM
api.add_resource(PODMProxy, '/<path:url>', endpoint='podmproxy')
