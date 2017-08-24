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

import copy
import unittest

import mock

from valence.common.exception import BadRequest
from valence.controller import podmanagers


class TestPodManagers(unittest.TestCase):

    @mock.patch('valence.controller.podmanagers.get_podm_list')
    def test_check_creation(self, mock_get_podm_list):
        mock_get_podm_list.return_value = [
            {"name": "test1",
             "url": "https://10.0.0.1"},
            {"name": "test2",
             "url": "https://10.0.0.2"}
        ]

        values = {"name": "podm_name",
                  "url": "https://10.240.212.123",
                  "authentication": [
                      {
                          "type": "basic",
                          "auth_items": {
                              "username": "xxxxxxx",
                              "password": "xxxxxxx"
                          }
                      }
                  ]}

        result_values = copy.deepcopy(values)
        result_values['driver'] = 'redfishv1'

        self.assertEqual(podmanagers._check_creation(values), result_values)
        mock_get_podm_list.assert_called_once_with()

    @mock.patch('valence.controller.podmanagers.get_podm_list')
    def test_check_creation_duplicate_Exception(self, mock_get_podm_list):
        mock_get_podm_list.return_value = [
            {"name": "test1",
             "url": "https://10.0.0.1",
             'authentication': "authentication"},
            {"name": "test2",
             "url": "https://10.0.0.2",
             'authentication': "authentication"
             }
        ]

        name_duplicate_values = {"name": "test1",
                                 "url": "https://10.240.212.123",
                                 'authentication': [
                                     {
                                         "type": "basic",
                                         "auth_items": {
                                             "username": "username",
                                             "password": "password"
                                         }
                                     }
                                 ]}
        url_duplicate_values = {"name": "podm_name",
                                "url": "https://10.0.0.2",
                                'authentication': [
                                    {
                                        "type": "basic",
                                        "auth_items": {
                                            "username": "username",
                                            "password": "password"
                                        }
                                    }
                                ]}

        self.assertRaises(BadRequest,
                          podmanagers._check_creation,
                          name_duplicate_values)
        self.assertRaises(BadRequest,
                          podmanagers._check_creation,
                          url_duplicate_values)
        self.assertEqual(mock_get_podm_list.call_count, 2)

    @mock.patch('valence.db.api.Connection.update_podmanager')
    def test_check_updation_ignore_url_uuid(self, mock_db_update):
        values = {
            "uuid": "uuid",
            "url": "url",
            "name": "name"
        }
        result_values = copy.deepcopy(values)
        result_values.pop('url')
        result_values.pop('uuid')

        podmanagers.update_podmanager('fake-podm-id', values)
        mock_db_update.assert_called_once_with('fake-podm-id', result_values)
