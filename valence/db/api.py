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


def get_connection():
    """Return a database connection instance"""
    return Connection()


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
