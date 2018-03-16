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

import datetime
import json
import os

import etcd

from valence.common import base
from valence.common import types
from valence import db


class ModelBase(base.ObjectBase):

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
            client = db.etcd_driver.get_driver().client

        path = self.etcd_path(self.uuid)

        if self.path_already_exist(client, path):
            # TODO(lin.a.yang): after exception module got merged, raise
            # valence specific DBResouceConflict exception here
            raise Exception(
                'Database resource conflict on {0}.'.format(path))

        client.write(path, json.dumps(self.as_dict()))

    def update(self, values, client=None):
        super(ModelBase, self).update(values)

        if not client:
            client = db.etcd_driver.get_driver().client

        path = self.etcd_path(self.uuid)

        if not self.path_already_exist(client, path):
            # TODO(lin.a.yang): after exception module got merged, raise
            # valence specific DBNotFound exception here
            raise Exception(
                'Database resource not found: {0}.'.format(path))

        client.write(path, json.dumps(self.as_dict()))

    def delete(self, client=None):
        if not client:
            client = db.etcd_driver.get_driver().client

        path = self.etcd_path(self.uuid)

        if not self.path_already_exist(client, path):
            # TODO(lin.a.yang): after exception module got merged, raise
            # valence specific DBNotFound exception here
            raise Exception(
                'Database resource not found: {0}.'.format(path))

        client.delete(path)


class ModelBaseWithTimeStamp(ModelBase):

    def __init__(self, *args, **kwargs):
        """Inject 'created_at' and 'updated_at' fields"""
        timestamp_fields = {
            'created_at': {
                'validate': types.Text.validate
            },
            'updated_at': {
                'validate': types.Text.validate
            }
        }
        self.fields.update(timestamp_fields)

        super(ModelBaseWithTimeStamp, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        """Update all timestamp fields when save new object

        Set current utc time to 'created_at' and 'updated_at' fields when
        save this key-value pair at the first time.
        """
        utcnow = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        self.created_at = utcnow
        self.updated_at = utcnow

        super(ModelBaseWithTimeStamp, self).save(*args, **kwargs)

    def update(self, *args, **kwargs):
        """Update 'updated_at' timestamp when udpate object

        Set current utc time to 'updated_at' field when update this
        key-value pair.
        """
        utcnow = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        self.updated_at = utcnow

        super(ModelBaseWithTimeStamp, self).update(*args, **kwargs)


class PodManager(ModelBaseWithTimeStamp):

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
        'driver': {
            'validate': types.Text.validate
        },
        'authentication': {
            'validate': types.List(types.Dict).validate
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
        'resource_uri': {
            'validate': types.Text.validate
        },
    }


class Flavor(ModelBaseWithTimeStamp):

    path = "/flavors"

    fields = {
        'uuid': {
            'validate': types.Text.validate
        },
        'name': {
            'validate': types.Text.validate
        },
        'properties': {
            'memory': {
                'capacity_mib': {
                    'validate': types.Text.validate
                },
                'type': {
                    'validate': types.Text.validate
                },
                'validate': types.Dict.validate
            },
            'processor': {
                'total_cores': {
                    'validate': types.Text.validate
                },
                'model': {
                    'validate': types.Text.validate
                },
                'validate': types.Dict.validate
            },
            'pci_device': {
                'type': {
                    'validate': types.List.validate
                },
                'validate': types.Dict.validate
            },
            'validate': types.Dict.validate
        }
    }


class ComposedNode(ModelBaseWithTimeStamp):

    path = "/nodes"

    fields = {
        'uuid': {
            'validate': types.Text.validate
        },
        'name': {
            'validate': types.Text.validate
        },
        'podm_id': {
            'validate': types.Text.validate
        },
        'index': {
            'validate': types.Text.validate
        },
        'resource_uri': {
            'validate': types.Text.validate
        },
        'managed_by': {
            'validate': types.Text.validate
        }
    }


class Device(ModelBaseWithTimeStamp):

    path = "/devices"

    fields = {
        'uuid': {
            'validate': types.Text.validate
        },
        'podm_id': {
            'validate': types.Text.validate
        },
        'node_id': {
            'validate': types.Text.validate
        },
        'type': {
            'validate': types.Text.validate
        },
        'pooled_group_id': {
            'validate': types.Text.validate
        },
        'state': {
            'validate': types.Text.validate
        },
        'properties': {
            'validate': types.Dict.validate
        },
        'extra': {
            'validate': types.Dict.validate
        },
        'resource_uri': {
            'validate': types.Text.validate
        }
    }
