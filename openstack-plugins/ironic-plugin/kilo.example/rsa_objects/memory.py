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
        """Return a list of memory objects.

        :param context: Security context.
        :param node_id:
        :param limit: maximum number of resources to return in a single result.
        :param marker: pagination marker for large data sets.
        :param sort_key: column to sort results by.
        :param sort_dir: direction to sort. "asc" or "desc".
        :param filters:
        :returns: a list of :class:`memory` object.

        """
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
        """Create a memory record in the DB.

        Column-wise updates will be made based on the result of
        self.what_changed(). If target_power_state is provided,
        it will be checked against the in-database copy of the
        memory before updates are made.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: memory(context)

        """
        values = self.obj_get_changes()
        db_memory = self.dbapi.create_memory(values)
        self._from_db_object(self, db_memory)

    @base.remotable_classmethod
    def destroy(cls, computer_system_id, context=None):
        """Delete the volume from the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: volume(context)
        :param pod_id: pod_id
        """
        cls.dbapi.destroy_mem(computer_system_id)

    @base.remotable
    def save(self, context=None):
        """Save updates to this memory.

        Updates will be made column by column based on the result
        of self.what_changed().

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: memory(context)
        """
        updates = self.obj_get_changes()
        self.dbapi.update_memory(self.url, updates)
        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        """Loads and applies updates for this memory.

        Loads a :class:`memory` with the same url from the database and
        checks for updated attributes. Updates are applied from
        the loaded memory column by column, if there are any updates.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: memory(context)
        """
        current = self.__class__.get_by_id(self._context, self.id)
        for field in self.fields:
            if (hasattr(self, base.get_attrname(field)) and
                        self[field] != current[field]):
                self[field] = current[field]
