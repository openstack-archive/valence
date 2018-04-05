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

import logging
import traceback

import flask_cors
import flask_restful
from six.moves import http_client

# Note: setup app needs to be called before the valence imports
# for config options initialization to take place.
from valence.api import app as flaskapp
app = flaskapp.get_app()  # noqa

import valence.api.root as api_root
import valence.api.v1.devices as v1_devices
import valence.api.v1.flavors as v1_flavors
import valence.api.v1.nodes as v1_nodes
import valence.api.v1.podmanagers as v1_podmanagers
import valence.api.v1.racks as v1_racks
import valence.api.v1.storages as v1_storages
import valence.api.v1.systems as v1_systems
import valence.api.v1.version as v1_version
from valence.common import exception
from valence.common import utils


LOG = logging.getLogger(__name__)
app = flaskapp.get_app()
cors = flask_cors.CORS(app)


class ValenceService(flask_restful.Api):
    """Overriding Flask Restful Error handler"""

    def handle_error(self, error):
        if issubclass(error.__class__, exception.ValenceError):
            LOG.debug(traceback.format_exc())
            return utils.make_response(error.status, error.as_dict())
        elif hasattr(error, 'status'):
            LOG.debug(traceback.format_exc())
            return utils.make_response(error.code,
                                       exception.httpexception(error))
        else:
            # Valence will not throw general exception in normal case, so use
            # LOG.error() to record it.
            LOG.error(traceback.format_exc())
            exc = exception.generalexception(error,
                                             http_client.INTERNAL_SERVER_ERROR)
            return utils.make_response(http_client.INTERNAL_SERVER_ERROR, exc)

api = ValenceService(app)

"""API V1.0 Operations"""

# API Root operation
api.add_resource(api_root.Root, '/', endpoint='root')

# V1 Root operations
api.add_resource(v1_version.V1, '/v1', endpoint='v1')

# Rack operations
api.add_resource(v1_racks.RackList, '/v1/racks', endpoint='racks')
api.add_resource(v1_racks.Rack, '/v1/racks/<string:rack_id>', endpoint='rack')

# Node(s) operations
api.add_resource(v1_nodes.Nodes, '/v1/nodes', endpoint='nodes')
api.add_resource(v1_nodes.Node,
                 '/v1/nodes/<string:node_uuid>',
                 endpoint='node')
api.add_resource(v1_nodes.NodeAction,
                 '/v1/nodes/<string:node_uuid>/action',
                 endpoint='node_action')
api.add_resource(v1_nodes.NodeManage, '/v1/nodes/manage',
                 endpoint='node_manage')
api.add_resource(v1_nodes.NodesStorage,
                 '/v1/nodes/<string:nodeid>/storages',
                 endpoint='nodes_storages')
api.add_resource(v1_nodes.NodeRegister,
                 '/v1/nodes/<string:node_uuid>/register',
                 endpoint='node_register')

# System(s) operations
api.add_resource(v1_systems.SystemsList, '/v1/systems', endpoint='systems')
api.add_resource(v1_systems.Systems, '/v1/systems/<string:systemid>',
                 endpoint='system')

# Flavor(s) operations
api.add_resource(v1_flavors.Flavors, '/v1/flavors', endpoint='flavors')
api.add_resource(v1_flavors.Flavor, '/v1/flavors/<string:flavorid>',
                 endpoint='flavor')

# Storage(s) operations
api.add_resource(v1_storages.StoragesList, '/v1/storages', endpoint='storages')
api.add_resource(v1_storages.Storages,
                 '/v1/storages/<string:storageid>', endpoint='storage')

# PodManager(s) operations
api.add_resource(v1_podmanagers.PodManager,
                 '/v1/pod_managers/<string:podm_uuid>', endpoint='podmanager')
api.add_resource(v1_podmanagers.PodManagersList,
                 '/v1/pod_managers', endpoint='podmanagers')

# Device(s) operations
api.add_resource(v1_devices.PooledDevicesList, '/v1/devices',
                 endpoint='devices')
api.add_resource(v1_devices.PooledDevices, '/v1/devices/<string:device_id>',
                 endpoint='device')
api.add_resource(v1_devices.SyncResources, '/v1/devices/sync', endpoint='sync')

# Proxy to PODM
api.add_resource(api_root.PODMProxy, '/<path:url>', endpoint='podmproxy')
