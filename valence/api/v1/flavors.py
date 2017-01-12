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

from valence import flavors
from valence.common import utils

LOG = logging.getLogger(__name__)


class Flavors(Resource):

    def get(self):
        return utils.make_response(http_client.OK, flavors.list_flavors())

    def post(self):
        return flavors.create_flavor(request.get_json())

    def delete(self, flavorid):
        return flavors.delete_flavor(flavorid)

    def patch(self, flavorid):
        return flavors.update_flavor(flavorid, request.get_json())
