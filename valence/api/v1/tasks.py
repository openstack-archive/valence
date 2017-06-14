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

from flask_restful import Resource
from six.moves import http_client

from valence.common import utils
from valence.controller import tasks

LOG = logging.getLogger(__name__)


class Task(Resource):

    def get(self, taskid):
        return utils.make_response(http_client.OK,
                                   tasks.get_task(taskid))

    def delete(self, taskid):
        return utils.make_response(http_client.OK,
                                   tasks.delete_task(taskid))


class Tasks(Resource):

    def get(self):
        return utils.make_response(http_client.OK, tasks.list_tasks())
