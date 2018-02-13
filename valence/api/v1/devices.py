# Copyright (c) 2017 NEC, Corp.
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

from flask import request
from flask_restful import Resource
from six.moves import http_client

from valence.common import utils
from valence.controller import pooled_devices

LOG = logging.getLogger(__name__)


class PooledDevicesList(Resource):

    def get(self):
        filters = request.args.to_dict()
        return utils.make_response(http_client.OK,
                                   pooled_devices.PooledDevices.list_devices(
                                       filters))


class PooledDevices(Resource):

    def get(self, resource_id):
        return utils.make_response(http_client.OK,
                                   pooled_devices.PooledDevices.get_device(
                                       resource_id))


class SyncResources(Resource):

    def post(self):
        podm_id = request.get_json().get('podm_id', None)
        return utils.make_response(
            http_client.OK,
            pooled_devices.PooledDevices.synchronize_devices(podm_id))
