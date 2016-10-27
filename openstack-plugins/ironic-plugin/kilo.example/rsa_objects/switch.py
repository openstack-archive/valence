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


class Switch(base.IronicObject):
    dbapi = dbapi.get_instance()

    fields = {
        'id': int,
        'pod_id': obj_utils.str_or_none,
        'name': obj_utils.str_or_none,
        'description': obj_utils.str_or_none,
        'url': obj_utils.str_or_none,  # SwitchId in the rsa PSME api spec doc
        'manufacturer': obj_utils.str_or_none,
        'manufactueing_date': obj_utils.str_or_none,
        'model': obj_utils.str_or_none,
        'serial_number': obj_utils.str_or_none,
        'part_number': obj_utils.str_or_none,
        'firmware_name': obj_utils.str_or_none,
        'firmware_version': obj_utils.str_or_none,
        'status': obj_utils.str_or_none,
        'location': obj_utils.str_or_none,
    }

    @staticmethod
    def _from_db_object(switch, db_switch):
        for field in switch.fields:
            switch[field] = db_switch[field]
        switch.obj_reset_changes()
        return switch

    @base.remotable_classmethod
    def get_by_id(cls, context, switch_id):
        db_switch = cls.dbapi.get_switch_by_id(switch_id)
        switch = Switch._from_db_object(cls(context), db_switch)
        return switch

    @base.remotable_classmethod
    def get_by_url(cls, context, url):
        db_chassis = cls.dbapi.get_switch_by_url(url)
        chassis = Switch._from_db_object(cls(context), db_chassis)
        return chassis

    @base.remotable_classmethod
    def list_by_pod_id(cls, context, pod_id, limit=None, marker=None,
                       sort_key=None, sort_dir=None):
        db_switch = cls.dbapi.get_pod_switch_list(pod_id, limit=limit,
                                                  marker=marker,
                                                  sort_key=sort_key,
                                                  sort_dir=sort_dir)
        return [Switch._from_db_object(cls(context), obj) for obj in db_switch]

    @base.remotable
    def create(self, context=None):
        values = self.obj_get_changes()
        db_switch = self.dbapi.create_switch(values)
        self._from_db_object(self, db_switch)

    @base.remotable_classmethod
    def destroy(cls, pod_id, context=None):
        cls.dbapi.destroy_switch(pod_id)

    @base.remotable
    def save(self, context=None):
        updates = self.obj_get_changes()
        self.dbapi.update_switch(self.url, updates)
        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        current = self.__class__.get_by_id(self._context, self.id)
        for field in self.fields:
            if hasattr(self, base.get_attrname(field)):
                if self[field] != current[field]:
                    self[field] = current[field]
