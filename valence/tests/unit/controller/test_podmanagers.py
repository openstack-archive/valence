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

from requests import auth

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

    def test_get_basic_auth_from_authentication(self):
        authentication = [
            {
                "type": "basic",
                "auth_items": {
                    "username": "username",
                    "password": "password"
                }
            },
            {
                "type": "DynamicCode",
                "auth_items": {
                    "code": "xxxxxxx"
                }
            }
        ]
        value = podmanagers.get_basic_auth_from_authentication(authentication)
        self.assertEqual(auth.HTTPBasicAuth('username', 'password'), value)

    def test_get_basic_auth_from_authentication_none_basic_auth(self):
        authentication = [
            {
                "type": "DynamicCode",
                "auth_items": {
                    "code": "xxxxxxx"
                }
            },
            {
                "type": "CertificateAuthority",
                "auth_items": {
                    "public_key": "xxxxxxx"
                }
            }
        ]
        value = podmanagers.get_basic_auth_from_authentication(authentication)
        self.assertIsNone(value)

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
        mock_pod_status.asset_called_once_with('url', authentication)

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

    @mock.patch('valence.controller.podmanagers.'
                'get_basic_auth_from_authentication')
    @mock.patch('valence.common.http_adapter.get_http_request')
    def test_get_podm_usage(self, get_http_mock, get_basic_auth_mock):
        podm = {
            "uuid": "uuid",
            "url": "https://10.24.212.184:8443",
            "authentication": [
                {
                    "type": "basic",
                    "auth_items": {
                        "username": "username",
                        "password": "password"
                    }
                }
            ]
        }
        get_basic_auth_mock.return_value = 'basic_auth'
        get_http_mock.side_effect = [
            {
                "Name": "Computer System Collection",
                "Members@odata.count": 16
            },
            {
                "Name": "Composed Nodes Collection",
                "Members@odata.count": 7
            }
        ]
        result = {
            "podm_uuid": "uuid",
            "systems": 16,
            "nodes": 7,
            "usage": float("%.2f" % (7.0 / 16))
        }
        self.assertEqual(result, podmanagers.get_podm_usage(podm))
        self.assertEqual(get_http_mock.call_count, 2)
        get_basic_auth_mock.asset_called_once_with(podm['authentication'])

    @mock.patch('valence.controller.podmanagers.get_podm_list')
    def test_schedule_podm_none_online_podms(self, get_podm_list_mock):
        get_podm_list_mock.return_value = [
            {
                "uuid": "uuid1",
                "name": "pod1",
                "status": constants.PODM_STATUS_OFFLINE
            },
            {
                "uuid": "uuid2",
                "name": "pod2",
                "status": constants.PODM_STATUS_UNKNOWN
            }
        ]
        self.assertIsNone(podmanagers.schedule_podm())

    @mock.patch('valence.controller.podmanagers.get_podm_by_uuid')
    @mock.patch('valence.controller.podmanagers.get_podm_usage')
    @mock.patch('valence.controller.podmanagers.get_podm_list')
    def test_schedule_podm(self,
                           get_podm_list_mock,
                           get_podm_usage_mock,
                           get_podm_by_uuid_mock):
        get_podm_list_mock.return_value = [
            {
                "uuid": "uuid1",
                "name": "pod1",
                "status": constants.PODM_STATUS_ONLINE
            },
            {
                "uuid": "uuid2",
                "name": "pod2",
                "status": constants.PODM_STATUS_UNKNOWN
            },
            {
                "uuid": "uuid3",
                "name": "pod3",
                "status": constants.PODM_STATUS_ONLINE
            },
            {
                "uuid": "uuid4",
                "name": "pod4",
                "status": constants.PODM_STATUS_ONLINE
            },
        ]

        get_podm_usage_mock.side_effect = [
            {
                "podm_uuid": "uuid1",
                "systems": 16,
                "nodes": 7,
                "usage": float("%.2f" % (7.0 / 16))
            },
            {
                "podm_uuid": "uuid3",
                "systems": 16,
                "nodes": 2,
                "usage": float("%.2f" % (2.0 / 16))
            },
            {
                "podm_uuid": "uuid4",
                "systems": 16,
                "nodes": 12,
                "usage": float("%.2f" % (12.0 / 16))
            }
        ]

        final_result_podm = {
            "uuid": "uuid3",
            "name": "pod3"
        }
        get_podm_by_uuid_mock.return_value = final_result_podm

        self.assertEqual(final_result_podm, podmanagers.schedule_podm())
        get_podm_list_mock.asset_called_once()
        self.assertEqual(get_podm_usage_mock.call_count, 3)
        get_podm_list_mock.asset_called_once_with('uuid3')
