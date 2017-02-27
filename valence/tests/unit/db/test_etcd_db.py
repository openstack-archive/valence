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

import unittest

import etcd
import mock

from valence.db import etcd_db


class TestDBInit(unittest.TestCase):

    def setUp(self):
        self.backup_directories = etcd_db.etcd_directories
        etcd_db.etcd_directories = ['/test']

    def tearDown(self):
        etcd_db.etcd_directories = self.backup_directories

    @mock.patch('etcd.Client.delete')
    @mock.patch('etcd.Client.write')
    @mock.patch('etcd.Client.read')
    def test_init_db(self, mock_etcd_read, mock_etcd_write, mock_etcd_delete):
        """Test init DB when no corresponding dir exists"""

        # Directory don't exist in etcd db
        mock_etcd_read.side_effect = etcd.EtcdKeyNotFound

        etcd_db.init_etcd_db()

        mock_etcd_read.assert_called_with('/test')
        mock_etcd_write.assert_called_with(
            '/test', None, dir=True, append=True)
        mock_etcd_delete.assert_not_called()

    @mock.patch('etcd.Client.delete')
    @mock.patch('etcd.Client.write')
    @mock.patch('etcd.Client.read')
    def test_init_db_with_existing_key(self, mock_etcd_read, mock_etcd_write,
                                       mock_etcd_delete):
        """Test init DB when a regular key with same name already exists"""

        # A regular key with same name already exists
        mock_etcd_read.return_value = mock.Mock(dir=False)

        etcd_db.init_etcd_db()

        mock_etcd_read.assert_called_with('/test')
        mock_etcd_write.assert_called_with(
            '/test', None, dir=True, append=True)
        mock_etcd_delete.assert_called_with('/test')

    @mock.patch('etcd.Client.delete')
    @mock.patch('etcd.Client.write')
    @mock.patch('etcd.Client.read')
    def test_init_db_with_existing_dir(self, mock_etcd_read, mock_etcd_write,
                                       mock_etcd_delete):
        """Test init DB when a dir with same name already exists"""

        # A dir with same name already exists
        mock_etcd_read.return_value = mock.Mock(dir=True)

        etcd_db.init_etcd_db()

        mock_etcd_read.assert_called_with('/test')
        mock_etcd_write.assert_not_called()
        mock_etcd_delete.assert_not_called()
