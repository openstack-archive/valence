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

from valence.common.exception import BadRequest
from valence.common import utils
from valence.podmanagers import podmanagers

LOG = logging.getLogger(__name__)


class PodManagersList(Resource):

    def get(self):
        LOG.debug("GET /pod_managers")
        return utils.make_response(200, podmanagers.get_podm_list())

    def post(self):
        LOG.debug("POST /pod_managers")
        values = request.get_json()
        if not (values['name'] and values['url'] and values['authentication']):
            LOG.error("Incomplete parameters")
            raise BadRequest(detail="Incomplete parameters")
        # check authentication's format and content
        try:
            if not (values['authentication'][0]['type'] and
                    values['authentication'][0]['auth_items']):
                LOG.error("invalid authentication when creating podmanager")
                raise BadRequest(detail="invalid authentication properties")
        except KeyError:
            LOG.error("Incomplete parameters when creating podmanager")
            raise BadRequest(detail="invalid authentication properties")

        return utils.make_response(200, podmanagers.create_podm(values))


class PodManager(Resource):

    def get(self, podm_uuid):
        LOG.debug("GET /pod_managers/" + podm_uuid)
        return utils.make_response(200,
                                   podmanagers.get_podm_by_uuid(podm_uuid))

    def patch(self, podm_uuid):
        LOG.debug("PATCH /pod_managers/" + podm_uuid)
        values = request.form.to_dict()
        return utils.make_response(200,
                                   podmanagers.update_podm(podm_uuid, values))

    def delete(self, podm_uuid):
        LOG.debug("DELETE /pod_managers/" + podm_uuid)
        podmanagers.delete_podm_by_uuid(podm_uuid)
