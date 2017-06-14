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

from valence.common import exception
from valence.common import utils
from valence.db import api as db_api

task_status = ["Created", "In Progress", "Complete", "Failed"]


class Task(object):

    def __init__(self):
        super(Task, self).__init__()

    @classmethod
    def list_tasks(cls):
        tasks = db_api.Connection.list_tasks()
        return [task.as_dict() for task in tasks]

    @classmethod
    def get_task(cls, task_uuid):
        task = db_api.Connection.get_task_by_uuid(task_uuid)
        return task.as_dict()

    @classmethod
    def create_task(cls, request, *args):
        values = dict()
        values['status'] = task_status[0]
        values['uuid'] = utils.generate_uuid()
        values['request_body'] = {'request_params': args}
        values['request'] = request
        task = db_api.Connection.create_task(values)
        return task.as_dict()

    @classmethod
    def delete_task(cls, task_uuid):
        db_api.Connection.delete_task(task_uuid)
        return exception.confirmation(
            confirm_code="DELETED",
            confirm_detail="This task {0} has been deleted successfully"
                           .format(task_uuid))

    @classmethod
    def update_task(cls, task_uuid, error=None):
        values = db_api.Connection.get_task_by_uuid(task_uuid)
        last_status = values['status']
        ind = task_status.index(last_status)
        new_values = dict()
        if ind < 2:
            if error:
                new_values['status'] = task_status[3]
                new_values['Failure_reason'] = str(error)
            else:
                new_status = task_status[(ind+1)]
                new_values['status'] = new_status
        task = db_api.Connection.update_task(task_uuid, new_values)
        return task.as_dict()
