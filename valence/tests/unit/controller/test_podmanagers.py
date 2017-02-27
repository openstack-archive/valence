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

from valence.common import constants
from valence.common.exception import BadRequest
from valence.controller import podmanagers


class TestPodManagers(unittest.TestCase):

    @mock.patch('valence.controller.podmanagers.get_podm_list')
    @mock.patch('valence.controller.podmanagers.get_podm_status')
    def test_check_creation(self, mock_get_podm_status, mock_get_podm_list):
        mock_get_podm_list.return_value = [
            {"name": "test1",
             "url": "https://10.0.0.1"},
            {"name": "test2",
             "url": "https://10.0.0.2"}
        ]
        mock_get_podm_status.return_value = constants.PODM_STATUS_ONLINE

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
        result_values['status'] = constants.PODM_STATUS_ONLINE

        self.assertEqual(podmanagers._check_creation(values), result_values)
        mock_get_podm_status.assert_called_once_with(values['url'],
                                                     values['authentication'])
        mock_get_podm_list.assert_called_once_with()

    def test_check_creation_incomplete_parameters(self):
        incomplete_values = {
            'name': 'name',
            'url': 'url'
        }
        self.assertRaises(BadRequest,
                          podmanagers._check_creation,
                          incomplete_values)

    def test_check_creation_invalid_authentication(self):
        invalid_authentication_values = {
            "name": "podm_name",
            "url": "https://10.0.0.2",
            'authentication': {
                "username": "username",
                "password": "password"
            }
        }
        self.assertRaises(BadRequest,
                          podmanagers._check_creation,
                          invalid_authentication_values)

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

    def test_check_updation_ignore_url_uuid(self):
        values = {
            "uuid": "uuid",
            "url": "url",
            "name": "name"
        }
        result_values = copy.deepcopy(values)
        result_values.pop('url')
        result_values.pop('uuid')

        self.assertEqual(podmanagers._check_updation(values), result_values)

    @mock.patch('valence.redfish.redfish.pod_status')
    def test_get_podm_status(self, mock_pod_status):
        mock_pod_status.return_value = constants.PODM_STATUS_ONLINE
        authentication = [
            {
                "type": "basic",
                "auth_items": {
                    "username": "username",
                    "password": "password"
                }
            }
        ]
        self.assertEqual(podmanagers.get_podm_status('url', authentication),
                         constants.PODM_STATUS_ONLINE)
        mock_pod_status.asset_called_once_with('url', "username", "password")

    def test_get_podm_status_unknown(self):
        """not basic type authentication podm status set value to be unknown"""
        authentication = [
            {
                "type": "CertificateAuthority",
                "auth_items": {
                    "public_key": "xxxxxxx"
                }
            },
            {
                "type": "DynamicCode",
                "auth_items": {
                    "code": "xxxxxxx"
                }
            }
        ]
        self.assertEqual(podmanagers.get_podm_status('url', authentication),
                         constants.PODM_STATUS_UNKNOWN)
