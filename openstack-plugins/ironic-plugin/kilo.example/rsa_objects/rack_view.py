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


class RackView(base.IronicObject):
    dbapi = dbapi.get_instance()

    fields = {
        'id': int,
        'rack_id': int,
        'begin_at': int,
        'height_U': int,
        'uri': obj_utils.str_or_none,
        'component_type': obj_utils.str_or_none,
    }

    @staticmethod
    def _from_db_object(rack_view, db_rack_view):
        """Converts a database entity to a formal object."""
        for field in rack_view.fields:
            rack_view[field] = db_rack_view[field]
        rack_view.obj_reset_changes()
        return rack_view

    @staticmethod
    def _from_db_object_list(db_objects, cls, context):
        """Converts a list of database entities to a list of formal objects."""
        return [RackView._from_db_object(cls(context), obj) for obj in db_objects]

    @base.remotable
    def get_rack_view_by_rack_id(self, cls, context, rack_id):
        db_rack_views = cls.dbapi.get_rack_view_by_rack_id(rack_id)
        return map(lambda rack_view: RackView._from_db_object(cls(context), rack_view), db_rack_views)

    @base.remotable
    def create(self, context=None):
        """Create a rack_view record in the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: rack_view(context)

        """
        values = self.obj_get_changes()
        db_rack_view = self.dbapi.create_rack_view(values)
        self._from_db_object(self, db_rack_view)

    @base.remotable
    def destroy(self, context=None):
        """Delete the rack_view from the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: rack_view(context)
        """
        self.dbapi.destroy_rack_view(self.uuid)
        self.obj_reset_changes()

    @base.remotable
    def save(self, context=None):
        """Save updates to this rack_view.

        Updates will be made column by column based on the result
        of self.what_changed().

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: rack_view(context)
        """
        updates = self.obj_get_changes()
        self.dbapi.update_rack_view(self.id, updates)
        self.obj_reset_changes()

