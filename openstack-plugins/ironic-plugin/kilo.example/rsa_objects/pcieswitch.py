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


class PCIeSwitch(base.IronicObject):
    dbapi = dbapi.get_instance()

    fields = {
        'id': int,
        'pod_id': int,
        'name': obj_utils.str_or_none,
        'url': obj_utils.str_or_none,
        'description': obj_utils.str_or_none,
        'status': obj_utils.str_or_none,
        'type': obj_utils.str_or_none,
    }

    @staticmethod
    def _from_db_object(pcieswitch, db_pcieswitch):
        """Converts a database entity to a formal object."""
        for field in pcieswitch.fields:
            pcieswitch[field] = db_pcieswitch[field]

        pcieswitch.obj_reset_changes()
        return pcieswitch

    @staticmethod
    def _from_db_object_list(db_objects, cls, context):
        """Converts a list of database entities to a list of formal objects."""
        return [PCIeSwitch._from_db_object(cls(context), obj) for obj in
                db_objects]

    @base.remotable_classmethod
    def get(cls, context, pcieswitch_id):
        """Find a pcieswitch based on its id or uuid and return a pcieswitch object.

        :param pcieswitch_id: the id *or* uuid of a pcieswitch.
        :returns: a :class:`pcieswitch` object.
        """
        if strutils.is_int_like(pcieswitch_id):
            return cls.get_by_id(context, pcieswitch_id)
        elif uuidutils.is_uuid_like(pcieswitch_id):
            return cls.get_by_uuid(context, pcieswitch_id)
        elif utils.is_valid_mac(pcieswitch_id):
            return cls.get_by_address(context, pcieswitch_id)
        else:
            raise exception.InvalidIdentity(identity=pcieswitch_id)

    @base.remotable_classmethod
    def get_by_id(cls, context, pcieswitch_id):
        """Find a pcieswitch based on its integer id and return a pcieswitch object.

        :param pcieswitch_id: the id of a pcieswitch.
        :returns: a :class:`pcieswitch` object.
        """
        db_pcieswitch = cls.dbapi.get_pcieswitch_by_id(pcieswitch_id)
        pcieswitch = PCIeSwitch._from_db_object(cls(context), db_pcieswitch)
        return pcieswitch

    @base.remotable_classmethod
    def get_by_url(cls, context, url):
        """Find a pcieswitch based on uuid and return a :class:`pcieswitch` object.

        :param url: the uuid of a pcieswitch.
        :param context: Security context
        :returns: a :class:`pcieswitch` object.
        """
        db_pcieswitch = cls.dbapi.get_pcieswitch_by_url(url)
        pcieswitch = PCIeSwitch._from_db_object(cls(context), db_pcieswitch)
        return pcieswitch

    @base.remotable_classmethod
    def list_by_pod(cls, context, pod_id, limit=None, marker=None,
                    sort_key=None, sort_dir=None):
        """Return a list of pcieswitch objects.

        :param context: Security context.
        :param type: Rack or Drawer
        :param pod_id: pod manager id
        :param limit: maximum number of resources to return in a single result.
        :param marker: pagination marker for large data sets.
        :param sort_key: column to sort results by.
        :param sort_dir: direction to sort. "asc" or "desc".
        :returns: a list of :class:`pcieswitch` object.

        """
        db_pcieswitch = cls.dbapi.get_pcieswitch_list_by_pod(pod_id,
                                                             limit=limit,
                                                             marker=marker,
                                                             sort_key=sort_key,
                                                             sort_dir=sort_dir)
        return PCIeSwitch._from_db_object_list(db_pcieswitch, cls, context)

    @base.remotable
    def create(self, context=None):
        """Create a pcieswitch record in the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: pcieswitch(context)

        """
        values = self.obj_get_changes()
        db_pcieswitch = self.dbapi.create_pcieswitch(values)
        self._from_db_object(self, db_pcieswitch)

    @base.remotable_classmethod
    def destroy(cls, pod_id, context=None):
        """Delete the pcieswitch from the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: pcieswitch(context)
        """
        cls.dbapi.destroy_pcieswitch(pod_id)

    @base.remotable
    def save(self, context=None):
        """Save updates to this pcieswitch.

        Updates will be made column by column based on the result
        of self.what_changed().

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: pcieswitch(context)
        """
        updates = self.obj_get_changes()
        self.dbapi.update_pcieswitch(self.url, updates)
        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        """Loads updates for this pcieswitch.

        Loads a pcieswitch with the same uuid from the database and
        checks for updated attributes. Updates are applied from
        the loaded pcieswitch column by column, if there are any updates.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: pcieswitch(context)
        """
        current = self.__class__.get_by_url(self._context, url=self.url)
        for field in self.fields:
            if (hasattr(self, base.get_attrname(field)) and
                        self[field] != current[field]):
                self[field] = current[field]
