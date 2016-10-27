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

from ironic.db import api as db_api
from ironic.objects import base
from ironic.objects import utils as obj_utils


class Manager(base.IronicObject):
    dbapi = db_api.get_instance()

    fields = {
        'id': int,
        'pod_id': obj_utils.str_or_none,
        'url': obj_utils.str_or_none,
        'uuid': obj_utils.str_or_none,
        'type': obj_utils.str_or_none,
        'name': obj_utils.str_or_none,
        'description': obj_utils.str_or_none,
        'model': obj_utils.str_or_none,
        'firmware_version': obj_utils.str_or_none,
        'graphical_console': obj_utils.str_or_none,
        'serial_console': obj_utils.str_or_none,
        'command_shell': obj_utils.str_or_none,
        'status': obj_utils.str_or_none,
    }

    @staticmethod
    def _from_db_object(manager, db_manager):
        """Converts a database entity to a formal object."""
        for field in manager.fields:
            manager[field] = db_manager[field]
        manager.obj_reset_changes()
        return manager

    @base.remotable_classmethod
    def get_by_id(cls, context, manager_id):
        db_manager = cls.dbapi.get_manager_by_id(manager_id)
        return Manager._from_db_object(cls(context), db_manager)

    @base.remotable_classmethod
    def get_by_url(cls, context, url):
        db_manager = cls.dbapi.get_manager_by_url(url)
        manager = Manager._from_db_object(cls(context), db_manager)
        return manager

    @base.remotable_classmethod
    def list_by_pod(cls, context, pod_id, limit=None, marker=None,
                    sort_key=None, sort_dir=None, ):
        db_managers = cls.dbapi.get_manager_list(pod_id=pod_id,
                                                 limit=limit,
                                                 marker=marker,
                                                 sort_key=sort_key,
                                                 sort_dir=sort_dir)
        return [Manager._from_db_object(cls(context), obj) for obj in
                db_managers]

    @base.remotable
    def create(self, context=None):
        values = self.obj_get_changes()
        db_manager = self.dbapi.create_manager(values)
        self._from_db_object(self, db_manager)

    @base.remotable
    def save(self, context=None):
        updates = self.obj_get_changes()
        self.dbapi.update_manager(self.id, updates)
        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        current = self.__class__.get_by_id(self._context, self.id)
        for field in self.fields:
            if hasattr(self, base.get_attrname(field)):
                if self[field] != current[field]:
                    self[field] = current[field]

    @base.remotable_classmethod
    def destroy(cls, pod_id, context=None):
        cls.dbapi.destroy_manager(pod_id)
