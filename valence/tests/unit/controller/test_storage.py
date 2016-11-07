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

import copy
import unittest

import mock

from valence.controller import storage
from valence.tests.unit.db import utils as test_utils
from valence.tests.unit.fakes import resource_fakes


class TestStorageController(unittest.TestCase):

    @mock.patch("valence.redfish.redfish.get_remote_drive")
    @mock.patch("valence.db.api.Connection.get_podm_resource_by_uuid")
    def test_get_storage_resource_by_uuid(
            self, mock_db_get_podm_resource, mock_redfish_get_drive):
        """Test get composed node detail"""
        storage_hw = resource_fakes.get_test_remote_drive()
        storage_db = test_utils.get_test_podm_resource()
        storage_db['resource_type'] = 'remote_drive'

        mock_db_model = mock.MagicMock()
        mock_db_model.as_dict.return_value = storage_db
        mock_db_get_podm_resource.return_value = mock_db_model

        mock_redfish_get_drive.return_value = storage_hw

        result = storage.Storage.get_storage_resource_by_uuid("fake_uuid")

        expected = copy.deepcopy(storage_hw)
        expected.update(storage_db)
        self.assertEqual(expected, result)

    @mock.patch("valence.db.api.Connection.delete_podm_resource")
    def test_delete_storage_resource(self,
                                     mock_db_delete_podm_resource):
        """Test delete composed node"""
        storage_db = test_utils.get_test_podm_resource()

        storage.Storage.delete_storage_resource(storage_db["uuid"])

        mock_db_delete_podm_resource.assert_called_once_with(
            storage_db["uuid"])

    @mock.patch("valence.db.api.Connection.list_podm_resources")
    def test_list_remote_drives(self, mock_db_list_podm_resources):
        """Test list all composed nodes"""
        drive_db = test_utils.get_test_podm_resource()

        mock_db_model = mock.MagicMock()
        mock_db_model.as_dict.return_value = drive_db
        mock_db_list_podm_resources.return_value = [mock_db_model]

        expected = [drive_db]

        result = storage.Storage.list_remote_drives()

        self.assertEqual(expected, result)
