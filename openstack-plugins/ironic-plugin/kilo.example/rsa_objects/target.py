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

from oslo_utils import strutils
from oslo_utils import uuidutils

from ironic.common import exception
from ironic.common import utils
from ironic.db import api as dbapi
from ironic.objects import base
from ironic.objects import utils as obj_utils


class RemoteTarget(base.IronicObject):
    dbapi = dbapi.get_instance()

    fields = {
        'id': int,
        'pod_id': int,
        'name': obj_utils.str_or_none,
        'url': obj_utils.str_or_none,
        'address': obj_utils.str_or_none,
        'port': int,
        'status': obj_utils.str_or_none,
    }

    @staticmethod
    def _from_db_object(target, db_target):
        """Converts a database entity to a formal object."""
        for field in target.fields:
            target[field] = db_target[field]

        target.obj_reset_changes()
        return target

    @staticmethod
    def _from_db_object_list(db_objects, cls, context):
        """Converts a list of database entities to a list of formal objects."""
        return [RemoteTarget._from_db_object(cls(context), obj) for obj in
                db_objects]

    @base.remotable_classmethod
    def get(cls, context, target_id):
        """Find a target based on its id or uuid and return a target object.

        :param target_id: the id *or* uuid of a target.
        :returns: a :class:`target` object.
        """
        if strutils.is_int_like(target_id):
            return cls.get_by_id(context, target_id)
        elif uuidutils.is_uuid_like(target_id):
            return cls.get_by_uuid(context, target_id)
        elif utils.is_valid_mac(target_id):
            return cls.get_by_address(context, target_id)
        else:
            raise exception.InvalidIdentity(identity=target_id)

    @base.remotable_classmethod
    def get_by_id(cls, context, target_id):
        """Find a target based on its integer id and return a target object.

        :param target_id: the id of a target.
        :returns: a :class:`target` object.
        """
        db_target = cls.dbapi.get_target_by_id(target_id)
        target = RemoteTarget._from_db_object(cls(context), db_target)
        return target

    @base.remotable_classmethod
    def get_by_url(cls, context, url):
        """Find a target based on uuid and return a :class:`target` object.

        :param url: the uuid of a target.
        :param context: Security context
        :returns: a :class:`target` object.
        """
        db_target = cls.dbapi.get_target_by_url(url)
        target = RemoteTarget._from_db_object(cls(context), db_target)
        return target

    @base.remotable_classmethod
    def list_by_pod(cls, context, pod_id, limit=None, marker=None,
                    sort_key=None, sort_dir=None):
        """Return a list of target objects.

        :param context: Security context.
        :param type: Rack or Drawer
        :param pod_id: pod manager id
        :param limit: maximum number of resources to return in a single result.
        :param marker: pagination marker for large data sets.
        :param sort_key: column to sort results by.
        :param sort_dir: direction to sort. "asc" or "desc".
        :returns: a list of :class:`target` object.

        """
        db_target = cls.dbapi.get_target_list_by_pod(pod_id,
                                                     limit=limit,
                                                     marker=marker,
                                                     sort_key=sort_key,
                                                     sort_dir=sort_dir)
        return RemoteTarget._from_db_object_list(db_target, cls, context)

    @base.remotable
    def create(self, context=None):
        """Create a target record in the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: target(context)

        """
        values = self.obj_get_changes()
        db_target = self.dbapi.create_target(values)
        self._from_db_object(self, db_target)

    @base.remotable_classmethod
    def destroy(cls, pod_id, context=None):
        """Delete the target from the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: target(context)
        """
        cls.dbapi.destroy_target(pod_id)

    @base.remotable
    def save(self, context=None):
        """Save updates to this target.

        Updates will be made column by column based on the result
        of self.what_changed().

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: target(context)
        """
        updates = self.obj_get_changes()
        self.dbapi.update_target(self.url, updates)
        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        """Loads updates for this target.

        Loads a target with the same uuid from the database and
        checks for updated attributes. Updates are applied from
        the loaded target column by column, if there are any updates.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: target(context)
        """
        current = self.__class__.get_by_url(self._context, url=self.url)
        for field in self.fields:
            if (hasattr(self, base.get_attrname(field)) and self[field] !=
                current[field]):
                self[field] = current[field]
