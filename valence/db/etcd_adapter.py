# Copyright 2016 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json

from etcd import EtcdKeyNotFound
from oslo_utils import uuidutils

from valence.db.etcd_db import etcd_client
from valence.db.etcd_db import etcd_directories
from valence.db.models.pod_manager import PodManager


class EtcdAdapter(object):
    dir_model_map = {
        "/v1/pod_managers": PodManager
    }

    def get_model_from_dir(self, directory):
        return self.dir_model_map[directory]

    def add_object(self, directory, **object_items):
        if directory not in etcd_directories:
            return "directory not found, invalid request"

        gen_uuid = uuidutils.generate_uuid()
        db_object = self.get_model_from_dir(directory).convert(**object_items)
        etcd_client.write(directory + '/' + gen_uuid, db_object)
        pod_info = self.get_object_by_uuid(directory, gen_uuid)
        return pod_info

    @staticmethod
    def update_object(key, **update_items):
        db_object = etcd_client.read(key)
        # update the object's value properties
        db_object_value = json.loads(db_object.value)
        for k, v in update_items.items():
            db_object_value[k] = v
        # reassignment the object's value then update the whole object
        db_object.value = db_object_value
        etcd_client.update(db_object)

    @staticmethod
    def get_object_list(directory):
        if directory not in etcd_directories:
            return "directory not found, invalid request"

        try:
            object_list = etcd_client.read(directory)
            return map(lambda x: x['value'], object_list._children)
        except EtcdKeyNotFound:
            return []

    @staticmethod
    def get_object_by_uuid(directory, uuid):
        if not uuidutils.is_uuid_like(uuid):
            return None
        try:
            object_info = etcd_client.read(directory + '/' + uuid).value
            return object_info
        except EtcdKeyNotFound:
            return None
