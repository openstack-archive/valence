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

from valence.db.etcd_adapter import EtcdAdapter
from datetime import datetime
import requests


def get_podm_list():
    pass


def get_podm_by_uuid(uuid):
    return EtcdAdapter.get_object_by_uuid('/v1/pod_managers', uuid)


def update_podm(uuid, **update_items):
    key = '/v1/pod_managers/' + uuid
    if _check(update_items):
        update_items['updated_at'] = str(datetime.now())
        return EtcdAdapter.update_object(key, **update_items)


def create_podm(**podm_items):
    pass


def delete_podm_by_uuid(uuid):
    return EtcdAdapter.delete_object_by_uuid('/v1/pod_managers', uuid)


def _check(items):
    # check not null
    fileds = ['name', 'url', 'auth']
    values = [i.value for i in items if i in fileds]
    if not all(values):
        return "please check your args, 'name/url/auth/' can't be null"

    # check url status
    try:
        requests.get(items['url'], auth=items['auth'])
        status = 'Online'
    except requests.ConnectionError:
        status = 'Offline'

    return True

