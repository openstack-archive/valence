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

from unittest import TestCase

import mock

from valence.common import exception
from valence.controller import flavors
from valence.tests.unit.fakes import flavor_fakes as fakes


class TestFlavors(TestCase):

    @mock.patch('valence.db.api.Connection.list_flavors')
    def test_list_flavors(self, mock_db_list_flavors):
        mock_db_list_flavors.return_value = fakes.fake_flavor_model_list()
        result = flavors.list_flavors()
        self.assertEqual(fakes.fake_flavor_list(), result)

    @mock.patch('valence.db.api.Connection.create_flavor')
    def test_create_flavor(self, mock_db_create_flavor):
        mock_db_create_flavor.return_value = fakes.fake_flavor_model()
        result = flavors.create_flavor(fakes.fake_flavor())
        self.assertEqual(fakes.fake_flavor(), result)

    @mock.patch('valence.db.api.Connection.delete_flavor')
    def test_delete_flavor(self, mock_db_delete_flavor):
        expected = exception.confirmation(
            confirm_code="DELETED",
            confirm_detail="This flavor {0} has been deleted successfully"
                           .format("00000000-0000-0000-0000-000000000000"))
        result = flavors.delete_flavor("00000000-0000-0000-0000-000000000000")
        self.assertEqual(expected, result)

    @mock.patch('valence.db.api.Connection.update_flavor')
    def test_update_flavor(self, mock_db_update_flavor):
        mock_db_update_flavor.return_value = fakes.fake_flavor_model()
        result = flavors.update_flavor(
            "00000000-0000-0000-0000-00000000",
            {"name": "Flavor 1"})
        self.assertEqual(fakes.fake_flavor(), result)
