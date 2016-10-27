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


class ComputerSystem(base.IronicObject):
    dbapi = db_api.get_instance()

    fields = {
        'id': int,
        'type': obj_utils.str_or_none,
        'uuid': obj_utils.str_or_none,
        'name': obj_utils.str_or_none,
        'description': obj_utils.str_or_none,
        'model': obj_utils.str_or_none,
        'hostname': obj_utils.str_or_none,
        'power_state': obj_utils.str_or_none,
        'status': obj_utils.str_or_none,
        'location': obj_utils.str_or_none,

        'url': obj_utils.str_or_none,
        'pod_id': obj_utils.int_or_none,
        'manager_id': obj_utils.int_or_none,

        'indicator_led': obj_utils.str_or_none,
        'asset_tag': obj_utils.str_or_none,
        'bios_version': obj_utils.str_or_none,
        'sku': obj_utils.str_or_none,
        'manufacturer': obj_utils.str_or_none,
        'serial_number': obj_utils.str_or_none,
        'part_number': obj_utils.str_or_none,
    }

    @staticmethod
    def _from_db_object(node, db_node):
        """Converts a database entity to a formal object."""
        for field in node.fields:
            node[field] = db_node[field]
        node.obj_reset_changes()
        return node

    @base.remotable_classmethod
    def get_by_id(cls, context, node_id):
        """Find a node based on its integer id and return a Node details
        info including cpu memory and disk.

        :param node_id: the id of a node.
        :returns: a :class:`Node` object.
        """
        db_node = cls.dbapi.get_computer_system_by_id(node_id)
        return ComputerSystem._from_db_object(cls(context), db_node)

    @base.remotable_classmethod
    def get_by_url(cls, context, url):
        """Find a node based on url and return a Node object.

        :param url: the url of a node.
        :returns: a :class:`Node` object.
        """
        db_node = cls.dbapi.get_computer_system_by_url(url)
        node = ComputerSystem._from_db_object(cls(context), db_node)
        return node

    @base.remotable_classmethod
    def list_by_pod(cls, context, pod_id, limit=None, marker=None,
                    sort_key=None, sort_dir=None, ):
        """Return a list of Node objects.filter_by pod_id

        :param pod_id: which pod scope
        :param context: Security context.
        :param limit: maximum number of resources to return in a single result.
        :param marker: pagination marker for large data sets.
        :param sort_key: column to sort results by.
        :param sort_dir: direction to sort. "asc" or "desc".
        :param filters: Filters to apply.
        :returns: a list of :class:`ComputerSystem` object.

        """
        db_nodes = cls.dbapi.get_computer_system_list(pod_id=pod_id,
                                                      limit=limit,
                                                      marker=marker,
                                                      sort_key=sort_key,
                                                      sort_dir=sort_dir)
        return [ComputerSystem._from_db_object(cls(context), obj) for obj in
                db_nodes]

    @base.remotable
    def create(self, context=None):
        """Create a Node record in the DB.

        Column-wise updates will be made based on the result of
        self.what_changed(). If target_power_state is provided,
        it will be checked against the in-database copy of the
        node before updates are made.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Node(context)

        """
        values = self.obj_get_changes()
        db_node = self.dbapi.create_computer_system(values)
        self._from_db_object(self, db_node)

    @base.remotable
    def save(self, context=None):
        """Save updates to this Node.

        Column-wise updates will be made based on the result of
        self.what_changed(). If target_power_state is provided,
        it will be checked against the in-database copy of the
        node before updates are made.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Node(context)
        """
        updates = self.obj_get_changes()
        self.dbapi.update_computer_system(self.id, updates)
        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        """Refresh the object by re-fetching from the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Node(context)
        """
        current = self.__class__.get_by_url(self._context, self.url)
        for field in self.fields:
            if (hasattr(self, base.get_attrname(field)) and
                        self[field] != current[field]):
                self[field] = current[field]

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
        cls.dbapi.destroy_computer_system(pod_id)
