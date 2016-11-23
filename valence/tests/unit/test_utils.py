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

from valence.common import utils


class TestUtils(TestCase):

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
