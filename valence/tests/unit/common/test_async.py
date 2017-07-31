# Copyright (c) 2018 NEC, Corp.
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

import futurist
import mock

from valence.common import async
from valence.common import exception


class AsyncTestCase(unittest.TestCase):
    def setUp(self):
        super(AsyncTestCase, self).setUp()
        self.executor = mock.Mock(spec=futurist.GreenThreadPoolExecutor)
        self.periodics = mock.Mock(spec=futurist.periodics.PeriodicWorker)
        async._executor = self.executor
        async._periodics_worker = self.periodics

    def test__spawn_worker(self):
        async._spawn_worker('fake', 1, foo='bar')
        self.executor.submit.assert_called_once_with('fake', 1, foo='bar')

    def test__spawn_worker_none_free(self):
        self.executor.submit.side_effect = futurist.RejectedSubmission()
        self.assertRaises(exception.ValenceException,
                          async._spawn_worker, 'fake')

    def test_start_periodic_tasks(self):
        fake_callable = mock.MagicMock()
        async.start_periodic_worker([(fake_callable, None, None)])
        self.executor.submit.assert_called_once_with(
            async._periodics_worker.start)

    def test_stop_periodic_tasks(self):
        async.stop_periodic_tasks()
        self.periodics.stop.assert_called()
        self.periodics.wait.assert_called()
        self.executor.shutdown.assert_called()
