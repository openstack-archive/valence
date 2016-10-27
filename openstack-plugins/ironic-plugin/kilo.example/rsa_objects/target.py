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
        db_target = cls.dbapi.get_target_by_id(target_id)
        target = RemoteTarget._from_db_object(cls(context), db_target)
        return target

    @base.remotable_classmethod
    def get_by_url(cls, context, url):
        db_target = cls.dbapi.get_target_by_url(url)
        target = RemoteTarget._from_db_object(cls(context), db_target)
        return target

    @base.remotable_classmethod
    def list_by_pod(cls, context, pod_id, limit=None, marker=None,
                    sort_key=None, sort_dir=None):
        db_target = cls.dbapi.get_target_list_by_pod(pod_id,
                                                     limit=limit,
                                                     marker=marker,
                                                     sort_key=sort_key,
                                                     sort_dir=sort_dir)
        return RemoteTarget._from_db_object_list(db_target, cls, context)

    @base.remotable
    def create(self, context=None):
        values = self.obj_get_changes()
        db_target = self.dbapi.create_target(values)
        self._from_db_object(self, db_target)

    @base.remotable_classmethod
    def destroy(cls, pod_id, context=None):
        cls.dbapi.destroy_target(pod_id)

    @base.remotable
    def save(self, context=None):
        updates = self.obj_get_changes()
        self.dbapi.update_target(self.url, updates)
        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        current = self.__class__.get_by_id(self._context, self.id)
        for field in self.fields:
            if hasattr(self, base.get_attrname(field)):
                if self[field] != current[field]:
                    self[field] = current[field]
