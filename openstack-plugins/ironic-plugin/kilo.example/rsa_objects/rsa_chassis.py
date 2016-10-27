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


class RSAChassis(base.IronicObject):
    dbapi = dbapi.get_instance()

    fields = {
        'id': int,
        'name': obj_utils.str_or_none,
        'type': obj_utils.str_or_none,
        'pod_id': int,
        'manager_id': int,
        'location': obj_utils.str_or_none,
        'url': obj_utils.str_or_none,
        'uuid': obj_utils.str_or_none,
        'description': obj_utils.str_or_none,
        'manufacturer': obj_utils.str_or_none,
        'model': obj_utils.str_or_none,
        'sku': obj_utils.str_or_none,
        'asset_tag': obj_utils.str_or_none,
        'serial_number': obj_utils.str_or_none,
        'part_number': obj_utils.str_or_none,
        'indicator_led': obj_utils.str_or_none,
        'status': obj_utils.str_or_none,
    }

    @staticmethod
    def _from_db_object(rsa_chassis, db_rsa_chassis):
        """Converts a database entity to a formal object."""
        for field in rsa_chassis.fields:
            rsa_chassis[field] = db_rsa_chassis[field]

        rsa_chassis.obj_reset_changes()
        return rsa_chassis

    @staticmethod
    def _from_db_object_list(db_objects, cls, context):
        """Converts a list of database entities to a list of formal objects."""
        return [RSAChassis._from_db_object(cls(context), obj) for obj in
                db_objects]

    @base.remotable_classmethod
    def get(cls, context, rsa_chassis_id):
        """
        Find a rsa_chassis based on its id or uuid and return a
        rsa_chassis object.

        :param rsa_chassis_id: the id *or* uuid of a rsa_chassis.
        :returns: a :class:`rsa_chassis` object.
        """
        if strutils.is_int_like(rsa_chassis_id):
            return cls.get_by_id(context, rsa_chassis_id)
        elif uuidutils.is_uuid_like(rsa_chassis_id):
            return cls.get_by_uuid(context, rsa_chassis_id)
        elif utils.is_valid_mac(rsa_chassis_id):
            return cls.get_by_address(context, rsa_chassis_id)
        else:
            raise exception.InvalidIdentity(identity=rsa_chassis_id)

    @base.remotable_classmethod
    def get_by_id(cls, context, rsa_chassis_id):
        """
        Find a rsa_chassis based on its integer id and return a
        rsa_chassis object.

        :param rsa_chassis_id: the id of a rsa_chassis.
        :returns: a :class:`rsa_chassis` object.
        """
        db_rsa_chassis = cls.dbapi.get_rsa_chassis_by_id(rsa_chassis_id)
        rsa_chassis = RSAChassis._from_db_object(cls(context), db_rsa_chassis)
        return rsa_chassis

    @base.remotable_classmethod
    def get_by_url(cls, context, url):
        """
        Find a rsa_chassis based on uuid and return a `rsa_chassis` object.

        :param url: the uuid of a rsa_chassis.
        :param context: Security context
        :returns: a :class:`rsa_chassis` object.
        """
        db_rsa_chassis = cls.dbapi.get_rsa_chassis_by_url(url)
        rsa_chassis = RSAChassis._from_db_object(cls(context), db_rsa_chassis)
        return rsa_chassis

    @base.remotable_classmethod
    def list_by_pod_and_type(cls, context, pod_id, type, limit=None,
                             marker=None, sort_key=None, sort_dir=None):
        """
        Return a list of rsa_chassis objects.

        :param context: Security context.
        :param type: Rack or Drawer
        :param pod_id: pod manager id
        :param limit: maximum number of resources to return in a single result.
        :param marker: pagination marker for large data sets.
        :param sort_key: column to sort results by.
        :param sort_dir: direction to sort. "asc" or "desc".
        :returns: a list of :class:`rsa_chassis` object.

        """
        db_rsa_chassis = \
            cls.dbapi.get_rsa_chassis_list_by_pod_and_type(pod_id,
                                                           type,
                                                           limit=limit,
                                                           marker=marker,
                                                           sort_key=sort_key,
                                                           sort_dir=sort_dir)
        return RSAChassis._from_db_object_list(db_rsa_chassis, cls, context)

    @base.remotable
    def create(self, context=None):
        """
        Create a rsa_chassis record in the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: rsa_chassis(context)

        """
        values = self.obj_get_changes()
        db_rsa_chassis = self.dbapi.create_rsa_chassis(values)
        self._from_db_object(self, db_rsa_chassis)

    @base.remotable_classmethod
    def destroy(cls, pod_id, chassis_type, context=None):
        """
        Delete the rsa_chassis from the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: rsa_chassis(context)
        """
        cls.dbapi.destroy_rsa_chassis(pod_id, chassis_type)

    @base.remotable
    def save(self, context=None):
        """
        Save updates to this rsa_chassis.

        Updates will be made column by column based on the result
        of self.what_changed().

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: rsa_chassis(context)
        """
        updates = self.obj_get_changes()
        self.dbapi.update_rsa_chassis(self.url, updates)
        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        """
        Loads updates for this rsa_chassis.

        Loads a rsa_chassis with the same uuid from the database and
        checks for updated attributes. Updates are applied from
        the loaded rsa_chassis column by column, if there are any updates.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: rsa_chassis(context)
        """
        current = self.__class__.get_by_url(self._context, url=self.url)
        for field in self.fields:
            if (hasattr(self, base.get_attrname(field)) and
                        self[field] != current[field]):
                self[field] = current[field]

    @base.remotable_classmethod
    def get_rack_resource(cls, pod_id, rack_id, context=None):
        """
        Return Rack resource sum.
        """
        sum = cls.dbapi.get_rack_resource(pod_id, rack_id)
        return sum

    @base.remotable_classmethod
    def get_chassis_computer_systems(cls, pod_id, chassis, chassis_id,
                                     context=None):
        """
        Return computer systems belong to this chassis.
        """
        systems = cls.dbapi.get_rack_computer_systems(pod_id, chassis,
                                                      chassis_id)
        computer_systems = []
        for system in systems:
            computer_system = dict()
            computer_system['system_name'] = system[0]
            computer_system['system_id'] = system[1]
            computer_system['system_location'] = eval(system[2])[
                'SystemLocation']
            computer_systems.append(computer_system)
        return computer_systems
