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

from valence.api.podmanagers import podmanagers
from valence.common import utils


LOG = logging.getLogger(__name__)


class PodManagersList(Resource):

    def get(self):
        return utils.make_response(http_client.OK, podmanagers.get_podm_list())

    def post(self):
        values = request.get_json()
        return utils.make_response(http_client.OK,
                                   podmanagers.create_podm(values))


class PodManager(Resource):

    def get(self, podm_uuid):
        return utils.make_response(http_client.OK,
                                   podmanagers.get_podm_by_uuid(podm_uuid))

    def patch(self, podm_uuid):
        values = request.form.to_dict()
        return utils.make_response(http_client.OK,
                                   podmanagers.update_podm(podm_uuid, values))

    def delete(self, podm_uuid):
        podmanagers.delete_podm_by_uuid(podm_uuid)
