# copyright (c) 2016 Intel, Inc.
#
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

"""
Base API interface for Database
"""

from valence.db import etcd_driver


def _get_driver():
    """Return a DB Driver instance."""
    return etcd_driver.get_driver()


class Connection(object):
    """Base class for database connections."""

    dbdriver = _get_driver()

    @classmethod
    def create_podmanager(cls, values):
        """Create a new pod manager.

        :values: The properties for this new pod manager.
        :returns: A pod manager created.
        """
        return cls.dbdriver.create_podmanager(values)

    @classmethod
    def get_podmanager_by_uuid(cls, podmanager_uuid):
        """Get specific pod manager by its uuid

        :param podmanager_uuid: The uuid of pod manager.
        :returns: A pod manager with this uuid.
        """
        return cls.dbdriver.get_podmanager_by_uuid(podmanager_uuid)

    @classmethod
    def delete_podmanager(cls, podmanager_uuid):
        """Delete specific pod manager by its uuid

        :param podmanager_uuid: The uuid of pod manager.
        """
        cls.dbdriver.delete_podmanager(podmanager_uuid)

    @classmethod
    def update_podmanager(cls, podmanager_uuid, values):
        """Update properties of a pod manager.

        :param podmanager_uuid: The uuid of pod manager.
        :values: The properties to be updated.
        :returns: A pod manager after updated.
        """
        return cls.dbdriver.update_podmanager(podmanager_uuid, values)

    @classmethod
    def list_podmanager(cls):
        """Get a list of all pod manager.

        :returns: A list of all pod managers.
        """
        return cls.dbdriver.list_podmanager()

    @classmethod
    def create_flavor(cls, values):
        """Create a new flavor.

        :param values: The properties of the new flavor.
        :returns: The created flavor.
        """
        return cls.dbdriver.create_flavor(values)

    @classmethod
    def get_flavor_by_uuid(cls, flavor_uuid):
        """Get specific flavor by its uuid.

        :param flavor_uuid: The uuid of the flavor.
        :returns: The flavor with the specified uuid.
        """
        return cls.dbdriver.get_flavor_by_uuid(flavor_uuid)

    @classmethod
    def delete_flavor(cls, flavor_uuid):
        """Delete a flavor by its uuid.

        :param flavor_uuid: The uuid of the flavor to delete.
        """
        cls.dbdriver.delete_flavor(flavor_uuid)

    @classmethod
    def update_flavor(cls, flavor_uuid, values):
        """Update properties of a specified flavor.

        :param flavor_uuid: The uuid of the flavor to update.
        :param values: The properties to be updated.
        :returns: The updated flavor.
        """
        return cls.dbdriver.update_flavor(flavor_uuid, values)

    @classmethod
    def list_flavors(cls):
        """Get a list of all flavors.

        :returns: A list of all flavors.
        """
        return cls.dbdriver.list_flavors()

    @classmethod
    def create_composed_node(cls, values):
        """Create a new composed node.

        :values: The properties for this new composed node.
        :returns: A composed node created.
        """
        return cls.dbdriver.create_composed_node(values)

    @classmethod
    def get_composed_node_by_uuid(cls, composed_node_uuid):
        """Get specific composed node by its uuid

        :param composed_node_uuid: The uuid of composed node.
        :returns: A composed node with this uuid.
        """
        return cls.dbdriver.get_composed_node_by_uuid(composed_node_uuid)

    @classmethod
    def delete_composed_node(cls, composed_node_uuid):
        """Delete specific composed node by its uuid

        :param composed_node_uuid: The uuid of composed node.
        """
        cls.dbdriver.delete_composed_node(composed_node_uuid)

    @classmethod
    def update_composed_node(cls, composed_node_uuid, values):
        """Update properties of a composed node.

        :param composed_node_uuid: The uuid of composed node.
        :values: The properties to be updated.
        :returns: A composed node model after updated.
        """
        return cls.dbdriver.update_composed_node(composed_node_uuid, values)

    @classmethod
    def list_composed_nodes(cls):
        """Get a list of all composed nodes.

        :returns: A list of all composed node.
        """
        return cls.dbdriver.list_composed_nodes()

    @classmethod
    def create_openstack_flavor(cls, values):
        """Create a new openstack flavor.

        :param values: The properties of the new flavor.
        :returns: The created flavor.
        """
        return cls.dbdriver.create_openstack_flavor(values)

    @classmethod
    def list_openstack_flavors(cls):
        """Get a list of all openstack flavors.

        :returns: A list of all flavors.
        """
        return cls.dbdriver.list_openstack_flavors()

    @classmethod
    def get_openstack_flavor_by_uuid(cls, flavoruuid):
        """Get specific flavor by its uuid.

        :param flavor_uuid: The uuid of the flavor.
        :returns: The flavor with the specified uuid.
        """
        return cls.dbdriver.get_openstack_flavor_by_uuid(flavoruuid)

    @classmethod
    def delete_openstack_flavor(cls, flavor_uuid):
        """Delete a flavor by its uuid.

        :param flavor_uuid: The uuid of the flavor to delete.
        """
        cls.dbdriver.delete_openstack_flavor(flavor_uuid)
