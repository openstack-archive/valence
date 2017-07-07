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

from six.moves import http_client

from valence.tests import FunctionalTest


class TestRootController(FunctionalTest):

    def test_root_get(self):
        response = self.app.get('/')
        assert response.status_code == http_client.OK

    def test_v1_get(self):
        response = self.app.get('/v1')
        assert response.status_code == http_client.OK
