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

from valence import config


etcd_directories = [
    "/v1/pod_managers"
]

etcd_client = etcd.Client(config.etcd_host, config.etcd_port)


def init_etcd_db():
    """initialize etcd database"""
    for directory in etcd_directories:
        etcd_client.write(directory, None, dir=True, append=True)
