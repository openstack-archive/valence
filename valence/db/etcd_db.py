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

import valence.conf
from valence.db import models


CONF = valence.conf.CONF

etcd_directories = [
    models.PodManager.path,
    models.Flavor.path,
    models.ComposedNode.path,
    models.Device.path
]

etcd_client = etcd.Client(CONF.etcd.host, CONF.etcd.port)


def init_etcd_db():
    """initialize etcd database"""
    for directory in etcd_directories:
        try:
            if not etcd_client.read(directory).dir:
                # This directory name already exists, but is regular file, not
                # directory, so delete it.
                etcd_client.delete(directory)
            else:
                # This directory already exists, so skip
                continue
        except etcd.EtcdKeyNotFound:
            # This directory name don't exist
            pass

        etcd_client.write(directory, None, dir=True, append=True)
