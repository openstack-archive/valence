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


class Interface(base.IronicObject):
    dbapi = dbapi.get_instance()

    fields = {
        'id': int,
        'name': obj_utils.str_or_none,
        'description': obj_utils.str_or_none,
        'mac_address': obj_utils.str_or_none,
        'ip_address': obj_utils.str_or_none,
        'status': obj_utils.str_or_none,
        'computer_system_id': obj_utils.int_or_none,
    }

    @staticmethod
    def _from_db_object(interface, db_interface):
        """Converts a database entity to a formal object."""
        for field in interface.fields:
            interface[field] = db_interface[field]
        interface.obj_reset_changes()
        return interface

    @staticmethod
    def _from_db_object_list(db_objects, cls, context):
        """Converts a list of database entities to a list of formal objects."""
        return [Interface._from_db_object(cls(context), obj) for obj in db_objects]

    @base.remotable_classmethod
    def get(cls, context, interface_id):
        """Find a interface based on its id or uuid and return a interface object.

        :param interface_id: the id *or* uuid of a interface.
        :returns: a :class:`interface` object.
        """
        if strutils.is_int_like(interface_id):
            return cls.get_by_id(context, interface_id)
        elif uuidutils.is_uuid_like(interface_id):
            return cls.get_by_uuid(context, interface_id)
        elif utils.is_valid_mac(interface_id):
            return cls.get_by_address(context, interface_id)
        else:
            raise exception.InvalidIdentity(identity=interface_id)

    @base.remotable_classmethod
    def get_by_id(cls, context, interface_id):
        """Find a interface based on its integer id and return a interface object.

        :param interface_id: the id of a interface.
        :returns: a :class:`interface` object.
        """
        db_interface = cls.dbapi.get_interface_by_id(interface_id)
        interface = Interface._from_db_object(cls(context), db_interface)
        return interface

    @base.remotable_classmethod
    def list_by_node_id(cls, context, node_id, limit=None, marker=None, sort_key=None, sort_dir=None):
        db_interface = cls.dbapi.get_node_interface_list(node_id, limit=limit, marker=marker, sort_key=sort_key,
                                                         sort_dir=sort_dir)
        return [Interface._from_db_object(cls(context), obj) for obj in db_interface]

    @base.remotable
    def create(self, context=None):
        """Create a interface record in the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: interface(context)

        """
        values = self.obj_get_changes()
        db_interface = self.dbapi.create_interface(values)
        self._from_db_object(self, db_interface)

    @base.remotable_classmethod
    def destroy(cls, computer_system_id, context=None):
        """Delete the interface from the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: interface(context)
        """
        cls.dbapi.destroy_interface(computer_system_id)

    @base.remotable
    def save(self, context=None):
        """Save updates to this interface.

        Updates will be made column by column based on the result
        of self.what_changed().

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: interface(context)
        """
        updates = self.obj_get_changes()
        self.dbapi.update_interface(self.id, updates)
        self.obj_reset_changes()
