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
        """Get a driver_instance_server record by its id.

        :param driver_instance_server_id: the id of a driver_instance_server
        :returns: a :class:`driver_instance_server` object.
        """
        db_obj = cls.dbapi.get_pod_manager_by_id(driver_instance_server_id)
        driver_instance_server = PodManager._from_db_object(
            cls(context), db_obj)
        return driver_instance_server

    @base.remotable_classmethod
    def get_by_ip(cls, context, ip):
        """Find a pod_manager based on url and return a Node object.

        :param url: the url of a manager.
        :returns: a :class:`pod_manager` object.
        """
        db_pod_manager = cls.dbapi.get_pod_manager_by_ip(ip)
        pod_manager = PodManager._from_db_object(cls(context), db_pod_manager)
        return pod_manager

    @base.remotable_classmethod
    def list(cls, context, limit=None, marker=None, sort_key=None, sort_dir=None, filters=None):
        """Return a list of XClarity objects.

        :param context: Security context.
        :param limit: maximum number of resources to return in a single result.
        :param marker: pagination marker for large data sets.
        :param sort_key: column to sort results by.
        :param sort_dir: direction to sort. "asc" or "desc".
        :param filters: Filters to apply.
        :returns: a list of :class:`XClarity` object.

        """
        db_driver_instance_servers = cls.dbapi.get_pod_manager_list(filters=filters,
                                                                    limit=limit,
                                                                    marker=marker,
                                                                    sort_key=sort_key,
                                                                    sort_dir=sort_dir)
        return [PodManager._from_db_object(cls(context), obj) for obj in db_driver_instance_servers]

    """
    do we need to provide a method to reserve a xclarity? 
    if one xclarity is in-active, do we need to reserve it?
    and, also the release
    """

    @base.remotable
    def create(self, context=None):
        """Create a driver_instance_server record in the DB.

        Column-wise updates will be made based on the result of
        self.what_changed(). 

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: driver_instance_server(context)

        """
        values = self.obj_get_changes()
        db_driver_instance_server = self.dbapi.create_pod_manager(values)
        self._from_db_object(self, db_driver_instance_server)

    @base.remotable_classmethod
    def destroy(cls, pod_id, context=None):
        """Delete the driver_instance_server from the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: driver_instance_server(context)
        """
        cls.dbapi.destroy_pod_manager(pod_id)

    @base.remotable
    def save(self, context=None):
        """Save updates to this driver_instance_server.

        Column-wise updates will be made based on the result of
        self.what_changed(). If target_power_state is provided,
        it will be checked against the in-database copy of the
        node before updates are made.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: driver_instance_server(context)
        """
        updates = self.obj_get_changes()
        self.dbapi.update_pod_manager(self.id, updates)
        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        """Refresh the object by re-fetching from the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: XClarity(context)
        """
        current = self.__class__.get_by_id(self._context, self.id)
        for field in self.fields:
            if hasattr(self, base.get_attrname(field)) and self[field] != current[field]:
                self[field] = current[field]
