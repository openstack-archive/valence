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


class Disk(base.IronicObject):
    dbapi = dbapi.get_instance()

    fields = {
        'id': int,
        'url': obj_utils.str_or_none,
        'type': obj_utils.str_or_none,
        'model': obj_utils.str_or_none,
        'size_gb': int,
        'serial_number': obj_utils.str_or_none,
        'volume_id': obj_utils.int_or_none,
        'computer_system_id': obj_utils.int_or_none,
    }

    @staticmethod
    def _from_db_object(disk, db_disk):
        for field in disk.fields:
            disk[field] = db_disk[field]

        disk.obj_reset_changes()
        return disk

    @base.remotable_classmethod
    def get_by_id(cls, context, disk_id):
        db_disk = cls.dbapi.get_disk_by_id(disk_id)
        disk = Disk._from_db_object(cls(context), db_disk)
        return disk

    @base.remotable_classmethod
    def get_by_url(cls, context, url):
        db_disk = cls.dbapi.get_disk_by_url(url)
        disk = Disk._from_db_object(cls(context), db_disk)
        return disk

    @base.remotable_classmethod
    def list_by_node_id(cls, context, node_id, limit=None, marker=None,
                        sort_key=None, sort_dir=None):
        db_disk = cls.dbapi.get_node_disk_list(node_id, limit=limit,
                                               marker=marker,
                                               sort_key=sort_key,
                                               sort_dir=sort_dir)
        return [Disk._from_db_object(cls(context), obj) for obj in db_disk]

    @base.remotable_classmethod
    def get_all_list(cls, context, limit=None, marker=None, sort_key=None,
                     sort_dir=None):
        db_disk = cls.dbapi.get_disk_list(limit=limit, marker=marker,
                                          sort_key=sort_key, sort_dir=sort_dir)
        return [Disk._from_db_object(cls(context), obj) for obj in db_disk]

    @base.remotable_classmethod
    def get_disk_sum_by_systems(cls, context, system_id_list):
        size_sum = cls.dbapi.get_disk_sum_by_systems(system_id_list)
        return size_sum

    @base.remotable
    def create(self, context=None):
        values = self.obj_get_changes()
        db_disk = self.dbapi.create_disk(values)
        self._from_db_object(self, db_disk)

    @base.remotable_classmethod
    def destroy(cls, computer_system_id, context=None):
        cls.dbapi.destroy_disk(computer_system_id)

    @base.remotable
    def save(self, context=None):
        updates = self.obj_get_changes()
        self.dbapi.update_disk(self.url, updates)
        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        current = self.__class__.get_by_id(self._context, self.id)
        for field in self.fields:
            if hasattr(self, base.get_attrname(field)):
                if self[field] != current[field]:
                    self[field] = current[field]
