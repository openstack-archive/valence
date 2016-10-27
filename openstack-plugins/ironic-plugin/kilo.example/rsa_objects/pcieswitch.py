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
        db_pcieswitch = cls.dbapi.get_pcieswitch_by_id(pcieswitch_id)
        pcieswitch = PCIeSwitch._from_db_object(cls(context), db_pcieswitch)
        return pcieswitch

    @base.remotable_classmethod
    def get_by_url(cls, context, url):
        db_pcieswitch = cls.dbapi.get_pcieswitch_by_url(url)
        pcieswitch = PCIeSwitch._from_db_object(cls(context), db_pcieswitch)
        return pcieswitch

    @base.remotable_classmethod
    def list_by_pod(cls, context, pod_id, limit=None, marker=None,
                    sort_key=None, sort_dir=None):
        db_pcieswitch = cls.dbapi.get_pcieswitch_list_by_pod(pod_id,
                                                             limit=limit,
                                                             marker=marker,
                                                             sort_key=sort_key,
                                                             sort_dir=sort_dir)
        return PCIeSwitch._from_db_object_list(db_pcieswitch, cls, context)

    @base.remotable
    def create(self, context=None):
        values = self.obj_get_changes()
        db_pcieswitch = self.dbapi.create_pcieswitch(values)
        self._from_db_object(self, db_pcieswitch)

    @base.remotable_classmethod
    def destroy(cls, pod_id, context=None):
        cls.dbapi.destroy_pcieswitch(pod_id)

    @base.remotable
    def save(self, context=None):
        updates = self.obj_get_changes()
        self.dbapi.update_pcieswitch(self.url, updates)
        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        current = self.__class__.get_by_url(self._context, url=self.url)
        for field in self.fields:
            if (hasattr(self, base.get_attrname(field)) and
                        self[field] != current[field]):
                self[field] = current[field]
