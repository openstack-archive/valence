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
from unittest import TestCase

from flask import Flask

from valence.common import utils


class TestMakeResponse(TestCase):

    def setUp(self):
        app = Flask(__name__)
        self.app_context = app.test_request_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_make_response(self):
        expect = {"key": "value"}
        resp = utils.make_response(expect)
        result = json.loads(resp.data.decode())
        self.assertEqual(expect, result)
        self.assertEqual(200, resp.status_code)

    def test_make_response_with_status_code(self):
        expect = {"key": "value"}
        resp = utils.make_response(expect, 404)
        result = json.loads(resp.data.decode())
        self.assertEqual(expect, result)
        self.assertEqual(404, resp.status_code)

    def test_make_response_with_wrong_status_code(self):
        with self.assertRaises(ValueError):
            utils.make_response(status_code="wrong_code")

    def test_make_response_with_headers(self):
        expect = {"key": "value"}
        resp = utils.make_response(expect, headers={"header": "header_value"})
        result = json.loads(resp.data.decode())
        self.assertEqual(expect, result)
        self.assertEqual(200, resp.status_code)
        self.assertEqual("header_value", resp.headers.get("header"))

    def test_make_response_with_wrong_headers(self):
        with self.assertRaises(ValueError):
            utils.make_response(headers=("header", "header_value"))
