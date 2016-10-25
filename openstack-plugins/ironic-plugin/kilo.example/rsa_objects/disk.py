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
    def list_by_node_id(cls, context, node_id, limit=None, marker=None, sort_key=None, sort_dir=None):
        """Return a list of disk objects.

        :param context: Security context.
        :param node_id:
        :param limit: maximum number of resources to return in a single result.
        :param marker: pagination marker for large data sets.
        :param sort_key: column to sort results by.
        :param sort_dir: direction to sort. "asc" or "desc".
        :returns: a list of :class:`disk` object.

        """
        db_disk = cls.dbapi.get_node_disk_list(node_id, limit=limit, marker=marker, sort_key=sort_key,
                                               sort_dir=sort_dir)
        return [Disk._from_db_object(cls(context), obj) for obj in db_disk]

    @base.remotable_classmethod
    def get_all_list(cls,context,limit=None, marker=None, sort_key=None, sort_dir=None):
        db_disk = cls.dbapi.get_disk_list(limit=limit, marker=marker, sort_key=sort_key, sort_dir=sort_dir)
        return [Disk._from_db_object(cls(context), obj) for obj in db_disk]

    @base.remotable_classmethod
    def get_disk_sum_by_systems(cls, context, system_id_list):
        size_sum = cls.dbapi.get_disk_sum_by_systems(system_id_list)
        return size_sum

    @base.remotable
    def create(self, context=None):
        """Create a disk record in the DB.

        Column-wise updates will be made based on the result of
        self.what_changed(). If target_power_state is provided,
        it will be checked against the in-database copy of the
        disk before updates are made.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: disk(context)

        """
        values = self.obj_get_changes()
        db_disk = self.dbapi.create_disk(values)
        self._from_db_object(self, db_disk)

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
        cls.dbapi.destroy_disk(computer_system_id)

    @base.remotable
    def save(self, context=None):
        """Save updates to this disk.

        Updates will be made column by column based on the result
        of self.what_changed().

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: disk(context)
        """
        updates = self.obj_get_changes()
        self.dbapi.update_disk(self.url, updates)
        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        """Loads and applies updates for this disk.

        Loads a :class:`disk` with the same url from the database and
        checks for updated attributes. Updates are applied from
        the loaded disk column by column, if there are any updates.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: disk(context)
        """
        current = self.__class__.get_by_url(self._context, url=self.url)
        for field in self.fields:
            if (hasattr(self, base.get_attrname(field)) and
                        self[field] != current[field]):
                self[field] = current[field]
