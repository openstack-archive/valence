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


from ironic.db import api as dbapi
from ironic.objects import base
from ironic.objects import utils as obj_utils


class Memory(base.IronicObject):
    dbapi = dbapi.get_instance()

    fields = {
        'id': int,
        'name': obj_utils.str_or_none,
        'url': obj_utils.str_or_none,
        'speed_mhz': obj_utils.int_or_none,
        'capacity_mb': obj_utils.int_or_none,
        'device_type': obj_utils.str_or_none,
        'serial_number': obj_utils.str_or_none,
        'part_number': obj_utils.str_or_none,
        'manufacturer': obj_utils.str_or_none,
        'computer_system_id': obj_utils.int_or_none,
    }

    @staticmethod
    def _from_db_object(memory, db_memory):
        for field in memory.fields:
            memory[field] = db_memory[field]
        memory.obj_reset_changes()
        return memory

    @base.remotable_classmethod
    def get_by_id(cls, context, memory_id):
        return cls.dbapi.get_memory_by_id(memory_id)

    @base.remotable_classmethod
    def get_by_url(cls, context, url):
        return cls.dbapi.get_memory_by_url(url)

    @base.remotable_classmethod
    def list_by_node_id(cls, context, node_id, limit=None, marker=None,
                        sort_key=None, sort_dir=None):
        db_memory = cls.dbapi.get_node_memory_list(node_id, limit=limit,
                                                   marker=marker,
                                                   sort_key=sort_key,
                                                   sort_dir=sort_dir)
        return [Memory._from_db_object(cls(context), obj) for obj in db_memory]

    @base.remotable_classmethod
    def get_all_list(cls, context, limit=None, marker=None, sort_key=None,
                     sort_dir=None):
        db_mem = cls.dbapi.get_mem_list(limit=limit, marker=marker,
                                        sort_key=sort_key, sort_dir=sort_dir)
        return [Memory._from_db_object(cls(context), obj) for obj in db_mem]

    @base.remotable_classmethod
    def get_memory_sum_by_systems(cls, context, system_id_list):
        mem_sum = cls.dbapi.get_mem_sum_by_systems(system_id_list)
        return mem_sum

    @base.remotable
    def create(self, context=None):
        values = self.obj_get_changes()
        db_memory = self.dbapi.create_memory(values)
        self._from_db_object(self, db_memory)

    @base.remotable_classmethod
    def destroy(cls, computer_system_id, context=None):
        cls.dbapi.destroy_mem(computer_system_id)

    @base.remotable
    def save(self, context=None):
        updates = self.obj_get_changes()
        self.dbapi.update_memory(self.url, updates)
        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        current = self.__class__.get_by_id(self._context, self.id)
        for field in self.fields:
            if (hasattr(self, base.get_attrname(field)) and
                        self[field] != current[field]):
                self[field] = current[field]
