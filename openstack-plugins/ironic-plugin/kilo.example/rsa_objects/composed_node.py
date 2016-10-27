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


class ComposedNode(base.IronicObject):
    dbapi = db_api.get_instance()

    fields = {
        'id': int,
        'name': obj_utils.str_or_none,
        'description': obj_utils.str_or_none,
        'url': obj_utils.str_or_none,
        'computer_system_id': int,
        'volume_id': obj_utils.str_or_none,
        'pod_id': int,
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
        db_node = cls.dbapi.get_composed_node_by_id(node_id)
        return ComposedNode._from_db_object(cls(context), db_node)

    @base.remotable_classmethod
    def get_by_volume_id(cls, context, volume_id):
        composed_node_info = cls.dbapi.get_by_volume_id(volume_id)
        return composed_node_info

    @base.remotable_classmethod
    def get_by_system_id(cls, context, system_id):
        db_node = cls.dbapi.get_composed_node_by_system_id(system_id)
        if db_node:
            return {'composed_node_name': db_node[0],
                    'composed_node_id': db_node[1]}
        else:
            return None

    @base.remotable_classmethod
    def get_by_url(cls, context, url):
        db_node = cls.dbapi.get_composed_node_by_url(url)
        node = ComposedNode._from_db_object(cls(context), db_node)
        return node

    @base.remotable_classmethod
    def list_by_pod(cls, context, pod_id, limit=None, marker=None,
                    sort_key=None, sort_dir=None, ):
        db_nodes = cls.dbapi.get_composed_node_list(pod_id=pod_id,
                                                    limit=limit,
                                                    marker=marker,
                                                    sort_key=sort_key,
                                                    sort_dir=sort_dir)
        return [ComposedNode._from_db_object(cls(context), obj) for obj in
                db_nodes]

    @base.remotable_classmethod
    def get_system_by_id(cls, context, pod_id):
        system_id_list = cls.dbapi.get_system_id_list(pod_id=pod_id)
        return system_id_list

    @base.remotable
    def create(self, context=None):
        values = self.obj_get_changes()
        db_node = self.dbapi.create_composed_node(values)
        self._from_db_object(self, db_node)

    @base.remotable
    def save(self, context=None):
        updates = self.obj_get_changes()
        self.dbapi.update_composed_node(self.id, updates)
        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        current = self.__class__.get_by_url(self._context, self.url)
        for field in self.fields:
            if (hasattr(self, base.get_attrname(field)) and
                        self[field] != current[field]):
                self[field] = current[field]

    @base.remotable_classmethod
    def destroy(cls, pod_id, context=None):
        cls.dbapi.destroy_composed_node(pod_id)
