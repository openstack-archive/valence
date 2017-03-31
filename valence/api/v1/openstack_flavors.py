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
from valence.controller import openstack_flavors

LOG = logging.getLogger(__name__)


class Openstack_Flavors(Resource):

    def post(self):
        return utils.make_response(http_client.OK,
                   openstack_flavors.create_flavor(request.get_json()))

    def get(self):
        return utils.make_response(http_client.OK,
                   openstack_flavors.list_flavors())

    def delete(self, flavoruuid):
        return utils.make_response(http_client.OK,
                                   openstack_flavors.delete_openstack_flavor(flavoruuid))

class Openstack_Flavors_Show(Resource):

    def get(self, flavoruuid):
        return utils.make_response(http_client.OK,
                   openstack_flavors.show_flavor(flavoruuid))  
                                                                                
class RegisterFlavor(Resource):
    def post(self, flavoruuid):
        return utils.make_response(http_client.OK,
                                   openstack_flavors.register(flavoruuid))

