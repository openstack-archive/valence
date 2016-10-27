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


class CPU(base.IronicObject):
    dbapi = dbapi.get_instance()

    fields = {
        'id': int,
        'name': obj_utils.str_or_none,
        'url': obj_utils.str_or_none,
        'speed_mhz': obj_utils.int_or_none,
        'model': obj_utils.str_or_none,
        'total_cores': obj_utils.int_or_none,
        'total_threads': obj_utils.int_or_none,
        'processor_type': obj_utils.str_or_none,
        'socket': obj_utils.str_or_none,
        'processor_architecture': obj_utils.str_or_none,
        'instruction_set': obj_utils.str_or_none,
        'manufacturer': obj_utils.str_or_none,
        'computer_system_id': obj_utils.int_or_none,
    }

    @staticmethod
    def _from_db_object(cpu, db_cpu):
        for field in cpu.fields:
            cpu[field] = db_cpu[field]
        cpu.obj_reset_changes()
        return cpu

    @base.remotable_classmethod
    def get_by_id(cls, context, cpu_id):
        db_cpu = cls.dbapi.get_cpu_by_id(cpu_id)
        cpu = CPU._from_db_object(cls(context), db_cpu)
        return cpu

    @base.remotable_classmethod
    def get_by_url(cls, context, url):
        db_cpu = cls.dbapi.get_cpu_by_url(url)
        cpu = CPU._from_db_object(cls(context), db_cpu)
        return cpu

    @base.remotable_classmethod
    def list_by_node_id(cls, context, node_id, limit=None, marker=None,
                        sort_key=None, sort_dir=None):
        db_cpu = cls.dbapi.get_node_cpu_list(node_id, limit=limit,
                                             marker=marker, sort_key=sort_key,
                                             sort_dir=sort_dir)
        return [CPU._from_db_object(cls(context), obj) for obj in db_cpu]

    @base.remotable_classmethod
    def get_all_list(cls, context, limit=None, marker=None, sort_key=None,
                     sort_dir=None):
        db_cpu = cls.dbapi.get_cpu_list(limit=limit, marker=marker,
                                        sort_key=sort_key, sort_dir=sort_dir)
        return [CPU._from_db_object(cls(context), obj) for obj in db_cpu]

    @base.remotable_classmethod
    def get_cpu_sum_by_systems(cls, context, system_id_list):
        size_sum = cls.dbapi.get_cpu_sum_by_systems(system_id_list)
        return size_sum

    @base.remotable
    def create(self, context=None):
        values = self.obj_get_changes()
        db_cpu = self.dbapi.create_cpu(values)
        self._from_db_object(self, db_cpu)

    @base.remotable_classmethod
    def destroy(cls, computer_system_id, context=None):
        cls.dbapi.destroy_cpu(computer_system_id)

    @base.remotable
    def save(self, context=None):
        updates = self.obj_get_changes()
        self.dbapi.update_cpu(self.url, updates)
        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        current = self.__class__.get_by_id(self._context, self.id)
        for field in self.fields:
            if hasattr(self, base.get_attrname(field) and
                            self[field] != current[field]):
                self[field] = current[field]
