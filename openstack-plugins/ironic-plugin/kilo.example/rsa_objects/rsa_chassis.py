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
        db_rsa_chassis = cls.dbapi.get_rsa_chassis_by_id(rsa_chassis_id)
        rsa_chassis = RSAChassis._from_db_object(cls(context), db_rsa_chassis)
        return rsa_chassis

    @base.remotable_classmethod
    def get_by_url(cls, context, url):
        db_rsa_chassis = cls.dbapi.get_rsa_chassis_by_url(url)
        rsa_chassis = RSAChassis._from_db_object(cls(context), db_rsa_chassis)
        return rsa_chassis

    @base.remotable_classmethod
    def list_by_pod_and_type(cls, context, pod_id, type, limit=None,
                             marker=None, sort_key=None, sort_dir=None):
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
        values = self.obj_get_changes()
        db_rsa_chassis = self.dbapi.create_rsa_chassis(values)
        self._from_db_object(self, db_rsa_chassis)

    @base.remotable_classmethod
    def destroy(cls, pod_id, chassis_type, context=None):
        cls.dbapi.destroy_rsa_chassis(pod_id, chassis_type)

    @base.remotable
    def save(self, context=None):
        updates = self.obj_get_changes()
        self.dbapi.update_rsa_chassis(self.url, updates)
        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        current = self.__class__.get_by_url(self._context, url=self.url)
        for field in self.fields:
            if (hasattr(self, base.get_attrname(field)) and
                        self[field] != current[field]):
                self[field] = current[field]

    @base.remotable_classmethod
    def get_rack_resource(cls, pod_id, rack_id, context=None):
        sum = cls.dbapi.get_rack_resource(pod_id, rack_id)
        return sum

    @base.remotable_classmethod
    def get_chassis_computer_systems(cls, pod_id, chassis, chassis_id,
                                     context=None):
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
