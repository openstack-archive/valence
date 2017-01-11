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

from valence.common import base
from valence.common import types


class TestTypes(unittest.TestCase):
    def test_text(self):
        self.assertIsNone(types.Text.validate(None))

        self.assertEqual('test_value', types.Text.validate('test_value'))
        self.assertRaises(ValueError,
                          types.Text.validate, 10)

    def test_string_type(self):
        self.assertIsNone(types.String.validate(None))

        test_value = 'test_value'
        self.assertEqual(test_value, types.String.validate(test_value))
        self.assertRaises(ValueError,
                          types.String.validate, 10)

        length = len(test_value)
        # test min_length
        self.assertEqual(test_value, types.String.validate(
            test_value, min_length=length - 1))
        self.assertEqual(test_value, types.String.validate(
            test_value, min_length=length))
        self.assertRaises(ValueError,
                          types.String.validate, test_value,
                          min_length=length + 1)

        # test max_length
        self.assertRaises(ValueError,
                          types.String.validate, test_value,
                          max_length=length - 1)
        self.assertEqual(test_value, types.String.validate(
            test_value, max_length=length))
        self.assertEqual(test_value, types.String.validate(
            test_value, max_length=length + 1))

    def test_integer_type(self):
        self.assertIsNone(types.Integer.validate(None))

        test_value = 10
        self.assertEqual(test_value, types.Integer.validate(test_value))
        self.assertEqual(test_value, types.Integer.validate('10'))
        self.assertRaises(ValueError,
                          types.Integer.validate, 'invalid')
        self.assertRaises(ValueError,
                          types.Integer.validate, '0.5')

        # test minimum
        self.assertEqual(test_value, types.Integer.validate(
            test_value, minimum=9))
        self.assertEqual(test_value, types.Integer.validate(
            test_value, minimum=10))
        self.assertRaises(ValueError,
                          types.Integer.validate, test_value,
                          minimum=11)

    def test_bool_type(self):
        self.assertTrue(types.Bool.validate(None, default=True))

        test_value = True
        self.assertEqual(test_value, types.Bool.validate(True))
        self.assertEqual(test_value, types.Bool.validate('True'))
        self.assertEqual(test_value, types.Bool.validate('true'))
        self.assertEqual(test_value, types.Bool.validate('t'))
        self.assertEqual(test_value, types.Bool.validate('yes'))
        self.assertEqual(test_value, types.Bool.validate('1'))

        test_value = False
        self.assertEqual(test_value, types.Bool.validate(False))
        self.assertEqual(test_value, types.Bool.validate('False'))
        self.assertEqual(test_value, types.Bool.validate('TTT'))
        self.assertEqual(test_value, types.Bool.validate(''))
        self.assertEqual(test_value, types.Bool.validate('0'))
        self.assertRaises(ValueError,
                          types.Bool.validate, None)
        self.assertRaises(ValueError,
                          types.Bool.validate, 0)

    def test_custom(self):
        class TestAPI(base.ObjectBase):
            fields = {
                'test': {
                    'validate': lambda v: v
                },
            }

        test_type = types.Custom(TestAPI)
        self.assertIsNone(test_type.validate(None))

        value = TestAPI(test='test_value')
        value = test_type.validate(value)
        self.assertIsInstance(value, TestAPI)
        self.assertEqual({'test': 'test_value'}, value.as_dict())

        test_type = types.Custom(TestAPI)
        value = test_type.validate({'test': 'test_value'})
        self.assertIsInstance(value, TestAPI)
        self.assertEqual({'test': 'test_value'}, value.as_dict())

        self.assertRaises(
            ValueError,
            test_type.validate, 'invalid_value')

    def test_list_with_text_type(self):
        list_type = types.List(types.Text)
        self.assertIsNone(list_type.validate(None))

        value = list_type.validate(['test1', 'test2'])
        self.assertEqual(['test1', 'test2'], value)

        self.assertRaises(
            ValueError,
            list_type.validate, 'invalid_value')

    def test_list_with_custom_type(self):
        class TestAPI(base.ObjectBase):
            fields = {
                'test': {
                    'validate': lambda v: v
                },
            }

        list_type = types.List(types.Custom(TestAPI))
        self.assertIsNone(list_type.validate(None))

        value = [{'test': 'test_value'}]
        value = list_type.validate(value)
        self.assertIsInstance(value, list)
        self.assertIsInstance(value[0], TestAPI)
        self.assertEqual({'test': 'test_value'}, value[0].as_dict())

    def test_dict_type(self):
        # Test default value
        self.assertEqual({}, types.Dict.validate(None))
        self.assertEqual({}, types.Dict.validate(None, default={}))

        # Test validate successfully
        self.assertEqual({"abc": "xyz"}, types.Dict.validate({"abc": "xyz"}))
        self.assertEqual({}, types.Dict.validate({}))

        # Test validate failed
        self.assertRaises(ValueError,
                          types.Dict.validate, "test")
        self.assertRaises(ValueError,
                          types.Dict.validate, 123)
        self.assertRaises(ValueError,
                          types.Dict.validate, [])
