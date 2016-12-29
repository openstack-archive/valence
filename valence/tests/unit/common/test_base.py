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

import unittest

from valence.tests.unit.fakes import common_fakes as fakes


class TestObjectBase(unittest.TestCase):

    def test_get_attr(self):
        expect = {"text": "value",
                  "integer": 123,
                  "bool": True}
        obj = fakes.FakeObject(**expect)
        self.assertEqual("value", obj["text"])
        self.assertEqual("value", obj.text)
        self.assertEqual(123, obj["integer"])
        self.assertEqual(123, obj.integer)
        self.assertEqual(True, obj["bool"])
        self.assertEqual(True, obj.bool)

    def test_validate_error(self):
        expect = {"text": "value",
                  "integer": "wrong_integer",
                  "bool": True}
        with self.assertRaises(ValueError) as context:
            fakes.FakeObject(**expect)

        self.assertTrue('Failed to convert value to int' in
                        str(context.exception))

    def test_render_to_dict(self):
        expect = {"text": "value",
                  "integer": 123,
                  "bool": True}
        obj = fakes.FakeObject(**expect)
        result = obj.as_dict()
        self.assertEqual(expect, result)

    def test_update_obj_attr(self):
        expect = {"text": "value",
                  "integer": 123,
                  "bool": True}
        obj = fakes.FakeObject(**expect)

        expect.update({"text": "another_value"})
        obj.update({"text": "another_value"})
        result = obj.as_dict()
        self.assertEqual(expect, result)
