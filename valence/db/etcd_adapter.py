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
import uuid

from etcd import EtcdKeyNotFound

from valence.db.etcd_db import etcd_client
from valence.db.etcd_db import etcd_directories
from valence.db.models.pod_manager import PodManager


class EtcdAdapter():
    dir_model_map = {
        "pod_manager": PodManager
    }

    def get_model_from_dir(self, directory):
        return self.dir_model_map[directory]

    def add_object(self, directory, **object_items):
        if directory not in etcd_directories:
            return "directory not found, invalid request"

        gen_uuid = uuid.uuid1()
        db_object = self.get_model_from_dir(directory).convert(**object_items)
        etcd_client.write(directory + '/' + gen_uuid, db_object)
        pod_info = self.get_object_by_uuid(directory, gen_uuid)
        return pod_info

    @staticmethod
    def update_object(key, **update_items):
        db_object = json.loads(etcd_client.read(key))
        for k, v in update_items.items():
            db_object[k] = v
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
        try:
            pod_info = etcd_client.read(directory + '/' + uuid).value
            return pod_info
        except EtcdKeyNotFound:
            return None
