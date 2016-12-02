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


from valence.db.etcd_db import etcd_client
from valence.db.etcd_db import etcd_directories
from valence.db.models.pod_manager import PodManager


class EtcdAdapter():
    dir_model_map = {
        "pod_manager": PodManager
    }

    def get_model_from_dir(self, directory):
        return self.dir_model_map[directory]

    def add_object(self, directory, **podm_items):
        if directory not in etcd_directories:
            return "directory not found, invalid request"

        uuid = ""
        db_object = self.get_model_from_dir(directory).convert(**podm_items)
        etcd_client.write(directory + '/' + uuid, db_object)
        pod_info = self.get_object_by_uuid(directory, uuid)
        return pod_info

    def update_object(self, directory, uuid, **update_items):
        pass
        # try:
        #     pod_info = self.etcd_client.read(directory + '/' + uuid)
        #     update_pod = json.loads(pod_info.value)
        #     for k, v in update_items.items():
        #         update_pod[k] = v
        #     pod_obj = PodProperty.convert(update_pod)
        # except Exception as e:
        #     return e
        # pod_info.value = pod_obj
        # etcd_client.update(pod_info)

    def get_object_list(self, directory):
        pass
        # try:
        #     value_list = etcd_client.read(directory)
        # except Exception as e:
        #     return e
        # pod_list = {}
        # for pod in value_list._children:
        #     if not pod.has_key('directory'):
        #         pod_list[pod['key']] = pod['value']
        # return pods_list

    def get_object_by_uuid(self, directory, uuid):
        try:
            pod_info = etcd_client.read(directory + '/' + uuid).value
        except Exception as ex:
            print ex  # TODO log
            return None
        return pod_info
