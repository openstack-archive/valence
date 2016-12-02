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

import etcd

etcd_client = etcd.Client(host, port)

def setup_db():
    pass


class EtcdAdapter():

    def add_object(dir, **object):
        dir_list = self.get_all_dirs()
	if dir in dir_list:
            uuid=""
	    etcd_client.write(dir+'/'+ uuid, object)
	    pod_info = self.get_object_by_uuid(dir, object['uuid'])
	    return pod_info
	else:
	    return 'dir not found'

    def update_object(dir, uuid, **update_items):
        try:
            pod_info = self.client.read(dir+'/'+uuid)
            update_pod = json.loads(pod_info.value)
            for k, v in update_items.items():
                update_pod[k] = v
            pod_obj = PodProperty.convert(update_pod)
        except Exception as e:
            return e
        pod_info.value = pod_obj
        etcd_client.update(pod_info)

    def get_object_list(dir):
    	try:
            value_list = etcd_client.read(dir)
        except Exception as e:
            return e
        pod_list = {}
        for pod in value_list._children:
	    if not pod.has_key('dir'):
                pod_list[pod['key']] = pod['value']
        return pods_list

    def get_object_by_uuid(dir, uuid):
	try:
            pod_info = etcd_client.read(dir+'/'+uuid).value
        except Exception as e:
            return e
        return pod_info

    def get_all_dirs():
	try:
	    value_list = etcd_client.read("/")
        except Exception as e:
            return e
	dir_list=[]
        for dir in value_list._children:
	    if dir.has_key('dir'):
	        dir_list.append(dir['key'])
	return dir_list
