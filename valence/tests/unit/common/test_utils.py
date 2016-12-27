# Copyright (c) 2016 Intel, Inc.
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

import json
import unittest

import flask
from six.moves import http_client

from valence.common import utils


class TestMakeResponse(unittest.TestCase):

    def setUp(self):
        app = flask.Flask(__name__)
        self.app_context = app.test_request_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_make_response(self):
        expect = {"key": "value"}
        resp = utils.make_response(http_client.OK, expect)
        result = json.loads(resp.data.decode())
        self.assertEqual(expect, result)
        self.assertEqual(http_client.OK, resp.status_code)

    def test_make_response_with_wrong_status_code(self):
        with self.assertRaises(ValueError):
            utils.make_response(status_code="wrong_code")

    def test_make_response_with_headers(self):
        expect = {"key": "value"}
        resp = utils.make_response(http_client.OK, expect,
                                   headers={"header": "header_value"})
        result = json.loads(resp.data.decode())
        self.assertEqual(expect, result)
        self.assertEqual(http_client.OK, resp.status_code)
        self.assertEqual("header_value", resp.headers.get("header"))

    def test_make_response_with_wrong_headers(self):
        with self.assertRaises(ValueError):
            utils.make_response(http_client.OK,
                                headers=("header", "header_value"))


class TestUtils(unittest.TestCase):

    def test_match_conditions(self):
        filter_condition = {"Id": "1"}
        json_content_pass = {"Name": "Pass",
                             "Id": "1"}
        result = utils.match_conditions(json_content_pass,
                                        filter_condition)
        self.assertTrue(result)
        json_content_fail = {"Name": "Fail",
                             "Id": "2"}
        result = utils.match_conditions(json_content_fail,
                                        filter_condition)
        self.assertFalse(result)
        json_content_fail_2 = {"Name": "Fail2"}
        result = utils.match_conditions(json_content_fail_2,
                                        filter_condition)
        self.assertFalse(result)

    def test_extract_val(self):
        data = {"Name": "NoMembers", "Id": 1, "Path": {
                "Level1": {"Level2": "L2"}}}
        result = utils.extract_val(data, "Id")
        self.assertEqual(result, 1)

        result = utils.extract_val(data, "Id1")
        self.assertEqual(result, None)

        result = utils.extract_val(data, "Path/Level1/Level2")
        self.assertEqual(result, "L2")

        result = utils.extract_val(data, "Id1", "DEFAULTID")
        self.assertEqual(result, "DEFAULTID")
