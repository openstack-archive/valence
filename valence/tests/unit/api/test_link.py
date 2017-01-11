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

from valence.api import link as link_module


class TestLink(unittest.TestCase):
    def test_build_url_with_bookmark(self):
        link = link_module.build_url(
            'v1', 'flavors', bookmark=True, base_url='http://localhost:8181')

        self.assertEqual('http://localhost:8181/v1/flavors', link)

    def test_build_url_without_bookmark(self):
        link = link_module.build_url(
            '', 'flavors', base_url='http://localhost:8181')

        self.assertEqual('http://localhost:8181/v1//flavors', link)

    def test_make_link(self):
        link = link_module.Link.make_link(
            'self', 'http://localhost:8181', 'v1', '',
            bookmark=True)

        expected_value = {
            'href': 'http://localhost:8181/v1/',
            'rel': 'self'
        }
        self.assertEqual(expected_value, link.as_dict())
