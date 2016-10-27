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


class Volume(base.IronicObject):
    dbapi = dbapi.get_instance()

    fields = {
        'id': int,
        'url': obj_utils.str_or_none,
        'name': obj_utils.str_or_none,
        'description': obj_utils.str_or_none,
        'mode': obj_utils.str_or_none,
        'size_GB': int,
        'pod_id': obj_utils.str_or_none,
        'type': obj_utils.str_or_none,
        'controller_id': int,
    }

    @staticmethod
    def _from_db_object(volume, db_volume):
        for field in volume.fields:
            volume[field] = db_volume[field]

        volume.obj_reset_changes()
        return volume

    @base.remotable_classmethod
    def get_by_id(cls, context, volume_id):
        db_volume = cls.dbapi.get_volume_by_id(volume_id)
        volume = Volume._from_db_object(cls(context), db_volume)
        return volume

    @base.remotable_classmethod
    def get_by_url(cls, context, url):
        db_volume = cls.dbapi.get_volume_by_url(url)
        volume = Volume._from_db_object(cls(context), db_volume)
        return volume

    @base.remotable_classmethod
    def list_by_pod_id(cls, context, pod_id, limit=None, marker=None,
                       sort_key=None, sort_dir=None):
        """Return a list of volume objects.

        :param context: Security context.
        :param pod_id:
        :param limit: maximum number of resources to return in a single result.
        :param marker: pagination marker for large data sets.
        :param sort_key: column to sort results by.
        :param sort_dir: direction to sort. "asc" or "desc".
        :returns: a list of :class:`volume` object.

        """
        db_volume = cls.dbapi.get_pod_volume_list(pod_id, limit=limit,
                                                  marker=marker,
                                                  sort_key=sort_key,
                                                  sort_dir=sort_dir)
        return [Volume._from_db_object(cls(context), obj) for obj in db_volume]

    @base.remotable
    def create(self, context=None):
        """Create a volume record in the DB.

        Column-wise updates will be made based on the result of
        self.what_changed(). If target_power_state is provided,
        it will be checked against the in-database copy of the
        volume before updates are made.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: volume(context)

        """
        values = self.obj_get_changes()
        db_volume = self.dbapi.create_volume(values)
        self._from_db_object(self, db_volume)

    @base.remotable_classmethod
    def destroy(cls, pod_id, context=None):
        """Delete the volume from the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: volume(context)
        :param pod_id: pod_id
        """
        cls.dbapi.destroy_volume(pod_id)

    @base.remotable
    def save(self, context=None):
        """Save updates to this volume.

        Updates will be made column by column based on the result
        of self.what_changed().

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: volume(context)
        """
        updates = self.obj_get_changes()
        self.dbapi.update_volume(self.url, updates)
        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        """Loads and applies updates for this volume.

        Loads a :class:`volume` with the same url from the database and
        checks for updated attributes. Updates are applied from
        the loaded volume column by column, if there are any updates.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: volume(context)
        """
        current = self.__class__.get_by_url(self._context, url=self.url)
        for field in self.fields:
            if (hasattr(self, base.get_attrname(field)) and
                        self[field] != current[field]):
                self[field] = current[field]
