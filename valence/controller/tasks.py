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

from valence.conductor.rpcapi import ComputeAPI as compute_api


def list_tasks():
    tasks = compute_api.list_tasks()
    return tasks


def get_task(taskid):
    task = compute_api.get_task(taskid)
    return task


def delete_task(taskid):
    res = compute_api.delete_task(taskid)
    return res
