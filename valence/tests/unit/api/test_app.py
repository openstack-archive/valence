# copyright (c) 2016 Intel, Inc.
#
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

import mock

import unittest

from valence.api import app


class TestApp(unittest.TestCase):

    @mock.patch('valence.config.PROJECT_NAME')
    @mock.patch('valence.api.app.flask.Flask')
    def test_setup_app_success(self, mock_Flask, mock_PROJECT_NAME):
        self.app = app.setup_app()
        mock_Flask.assert_called_with(mock_PROJECT_NAME)
        self.assertFalse(self.app.url_map.strict_slashes)
        self.app.logger.setLevel.assert_called_with(app.cfg.log_level)

    @mock.patch('valence.api.app.setup_app')
    def test_get_app_success(self, mock_setup_app):
        self._app = app.get_app()
        self.assertNotEqual(self._app, None)
