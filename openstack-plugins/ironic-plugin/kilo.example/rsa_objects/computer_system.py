# coding=utf-8
#
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

from ironic.db import api as db_api
from ironic.objects import base
from ironic.objects import utils as obj_utils


class ComputerSystem(base.IronicObject):
    dbapi = db_api.get_instance()

    fields = {
        'id': int,
        'type': obj_utils.str_or_none,
        'uuid': obj_utils.str_or_none,
        'name': obj_utils.str_or_none,
        'description': obj_utils.str_or_none,
        'model': obj_utils.str_or_none,
        'hostname': obj_utils.str_or_none,
        'power_state': obj_utils.str_or_none,
        'status': obj_utils.str_or_none,
        'location': obj_utils.str_or_none,

        'url': obj_utils.str_or_none,
        'pod_id': obj_utils.int_or_none,
        'manager_id': obj_utils.int_or_none,

        'indicator_led': obj_utils.str_or_none,
        'asset_tag': obj_utils.str_or_none,
        'bios_version': obj_utils.str_or_none,
        'sku': obj_utils.str_or_none,
        'manufacturer': obj_utils.str_or_none,
        'serial_number': obj_utils.str_or_none,
        'part_number': obj_utils.str_or_none,
    }

    @staticmethod
    def _from_db_object(node, db_node):
        """Converts a database entity to a formal object."""
        for field in node.fields:
            node[field] = db_node[field]
        node.obj_reset_changes()
        return node

    @base.remotable_classmethod
    def get_by_id(cls, context, node_id):
        db_node = cls.dbapi.get_computer_system_by_id(node_id)
        return ComputerSystem._from_db_object(cls(context), db_node)

    @base.remotable_classmethod
    def get_by_url(cls, context, url):

        db_node = cls.dbapi.get_computer_system_by_url(url)
        node = ComputerSystem._from_db_object(cls(context), db_node)
        return node

    @base.remotable_classmethod
    def list_by_pod(cls, context, pod_id, limit=None, marker=None,
                    sort_key=None, sort_dir=None, ):
        db_nodes = cls.dbapi.get_computer_system_list(pod_id=pod_id,
                                                      limit=limit,
                                                      marker=marker,
                                                      sort_key=sort_key,
                                                      sort_dir=sort_dir)
        return [ComputerSystem._from_db_object(cls(context), obj) for obj in
                db_nodes]

    @base.remotable
    def create(self, context=None):
        values = self.obj_get_changes()
        db_node = self.dbapi.create_computer_system(values)
        self._from_db_object(self, db_node)

    @base.remotable
    def save(self, context=None):
        updates = self.obj_get_changes()
        self.dbapi.update_computer_system(self.id, updates)
        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        current = self.__class__.get_by_url(self._context, self.url)
        for field in self.fields:
            if hasattr(self, base.get_attrname(field) and
                            self[field] != current[field]):
                self[field] = current[field]

    @base.remotable_classmethod
    def destroy(cls, pod_id, context=None):
        cls.dbapi.destroy_computer_system(pod_id)
