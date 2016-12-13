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

from valence.podmanagers import podmanagers

LOG = logging.getLogger(__name__)


class PodManagersList(Resource):
    def get(self):
        LOG.debug("GET /pod_managers")
        return podmanagers.get_podm_list()

    def post(self):
        LOG.debug("POST /pod_managers")
        podm_items = request.get_json()
        return podmanagers.create_podm(**podm_items)


class PodManager(Resource):
    def get(self, podm_id):
        LOG.debug("GET /pod_managers/" + podm_id)
        return podmanagers.get_podm_by_uuid(podm_id)

    def patch(self, podm_id):
        LOG.debug("PATCH /pod_managers/" + podm_id)
        podm_items = request.get_json()
        return podmanagers.update_podm(podm_id, **podm_items)

    def delete(self, podm_id):
        LOG.debug("DELETE /pod_managers/" + podm_id)
        return podmanagers.delete_podm_by_uuid(podm_id)
