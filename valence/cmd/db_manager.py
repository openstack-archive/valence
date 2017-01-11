#!/usr/bin/env python

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

import logging
import sys

import valence.db.etcd_db as valence_etcdb

LOG = logging.getLogger(__name__)


def init():
    valence_etcdb.init_etcd_db()


def migrate():
    pass


def main():
    if sys.argv[1] == 'init':
        LOG.info("initialize database")
        init()


if __name__ == '__main__':
    sys.exit(main())
