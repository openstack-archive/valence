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

import flask
import flask_restful
from six.moves import http_client

from valence.common import exception
from valence.common import utils
from valence.controller import podmanagers
from valence.validation import validator


LOG = logging.getLogger(__name__)


class PodManagersList(flask_restful.Resource):

    def get(self):
        return utils.make_response(http_client.OK, podmanagers.get_podm_list())

    @validator.check_input('podmanager_schema')
    def post(self):
        values = flask.request.get_json()
        return utils.make_response(http_client.OK,
                                   podmanagers.create_podmanager(values))


class PodManager(flask_restful.Resource):

    def get(self, podm_uuid):
        return utils.make_response(http_client.OK,
                                   podmanagers.get_podm_by_uuid(podm_uuid))

    def patch(self, podm_uuid):
        values = flask.request.get_json()
        return utils.make_response(http_client.OK,
                                   podmanagers.update_podmanager(podm_uuid,
                                                                 values))

    def delete(self, podm_uuid):
        podmanagers.delete_podmanager(podm_uuid)
        resp_dict = exception.confirmation(confirm_detail="DELETED")
        return utils.make_response(http_client.OK, resp_dict)
