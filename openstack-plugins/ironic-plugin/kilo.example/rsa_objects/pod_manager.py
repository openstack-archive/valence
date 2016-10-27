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


class PodManager(base.IronicObject):
    dbapi = db_api.get_instance()

    fields = {
        'id': int,
        'type': str,
        'name': str,
        'ipaddress': str,
        'username': str,
        'password': str,
        'url': str,
        'status': str,
        'inventory_status': str,
        'description': str
    }

    @staticmethod
    def _from_db_object(driver_instance_server, db_obj):
        """Converts a database entity to a formal object."""
        for field in driver_instance_server.fields:
            driver_instance_server[field] = db_obj[field]

        driver_instance_server.obj_reset_changes()
        return driver_instance_server

    @base.remotable_classmethod
    def get_by_id(cls, context, driver_instance_server_id):
        db_obj = cls.dbapi.get_pod_manager_by_id(driver_instance_server_id)
        driver_instance_server = PodManager._from_db_object(
            cls(context), db_obj)
        return driver_instance_server

    @base.remotable_classmethod
    def get_by_ip(cls, context, ip):
        db_pod_manager = cls.dbapi.get_pod_manager_by_ip(ip)
        pod_manager = PodManager._from_db_object(cls(context), db_pod_manager)
        return pod_manager

    @base.remotable_classmethod
    def list(cls, context, limit=None, marker=None, sort_key=None,
             sort_dir=None, filters=None):
        db_driver_instance_servers = cls.dbapi.get_pod_manager_list(
            filters=filters,
            limit=limit,
            marker=marker,
            sort_key=sort_key,
            sort_dir=sort_dir)
        return [PodManager._from_db_object(cls(context), obj) for obj in
                db_driver_instance_servers]

    @base.remotable
    def create(self, context=None):
        values = self.obj_get_changes()
        db_driver_instance_server = self.dbapi.create_pod_manager(values)
        self._from_db_object(self, db_driver_instance_server)

    @base.remotable_classmethod
    def destroy(cls, pod_id, context=None):
        cls.dbapi.destroy_pod_manager(pod_id)

    @base.remotable
    def save(self, context=None):
        updates = self.obj_get_changes()
        self.dbapi.update_pod_manager(self.id, updates)
        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        current = self.__class__.get_by_id(self._context, self.id)
        for field in self.fields:
            if hasattr(self, base.get_attrname(field)):
                if self[field] != current[field]:
                    self[field] = current[field]
