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

from flask import request
from flask_restful import Resource
from six.moves import http_client

from valence.common import utils
from valence.controller import systems

LOG = logging.getLogger(__name__)


class SystemsList(Resource):

    def get(self):
        req = request.get_json()
        filters = request.args.to_dict()
        return utils.make_response(
            http_client.OK,
            systems.System(req['podm_id']).list_systems(filters))


class Systems(Resource):

    def get(self, systemid):
        req = request.get_json()
        return utils.make_response(
            http_client.OK,
            systems.System(req['podm_id']).get_system_by_id(systemid))
