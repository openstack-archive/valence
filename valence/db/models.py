# copyright (c) 2016 Intel, Inc.
#
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

import os

import etcd

from valence.api import types
from valence.common import base
from valence.db import etcd_api


class ModelBase(base.ObjectBase):
    @classmethod
    def base_path(cls):
        return cls.path

    @classmethod
    def etcd_path(cls, sub_path):
        return os.path.normpath("/".join([cls.path, sub_path]))

    def path_already_exist(self, client, path):
        try:
            client.read(path)
        except etcd.EtcdKeyNotFound:
            return False

        return True

    def save(self, client=None):
        if not client:
            client = etcd_api.get_driver().client

        path = self.etcd_path(self.uuid)

        if self.path_already_exist(client, path):
            # TODO(lin.a.yang): after exception module got merged, raise
            # valence specific DBResouceConflict exception here
            raise Exception(
                'Database resource conflict on {0}.'.format(path))

        client.write(path, self.as_dict())

    def update(self, values, client=None):
        self.update(values)

        if not client:
            client = etcd_api.get_driver().client

        path = self.etcd_path(self.uuid)

        if not self.path_already_exist(client, path):
            # TODO(lin.a.yang): after exception module got merged, raise
            # valence specific DBNotFound exception here
            raise Exception(
                'Database resource not found: {0}.'.format(path))

        client.write(path, self.as_dict())

    def delete(self, client=None):
        if not client:
            client = etcd_api.get_driver().client

        path = self.etcd_path(self.uuid)

        if not self.path_already_exist(client, path):
            # TODO(lin.a.yang): after exception module got merged, raise
            # valence specific DBNotFound exception here
            raise Exception(
                'Database resource not found: {0}.'.format(path))

        client.delete(path)


class PodManager(ModelBase):

    path = "/pod_managers"

    fields = {
        'uuid': {
            'validate': types.Text.validate
        },
        'name': {
            'validate': types.Text.validate
        },
        'url': {
            'validate': types.Text.validate
        },
        'auth': {
            'validate': types.Text.validate
        },
        'status': {
            'validate': types.Text.validate
        },
        'description': {
            'validate': types.Text.validate
        },
        'location': {
            'validate': types.Text.validate
        },
        'redfish_link': {
            'validate': types.Text.validate
        },
        'bookmark_link': {
            'validate': types.Text.validate
        },
        'created_at': {
            'validate': types.Text.validate
        },
        'updated_at': {
            'validate': types.Text.validate
        }
    }
