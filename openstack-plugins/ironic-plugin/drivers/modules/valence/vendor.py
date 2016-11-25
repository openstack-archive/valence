# -*- encoding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


from oslo_log import log as logging

from ironic.drivers import base

LOG = logging.getLogger(__name__)


class ValenceVendor(base.VendorInterface):

    def get_properties(self):
        pass

    def validate(self, task, method, **kwargs):
        pass

    @base.driver_passthru(['POST'], async=False)
    def test_connection(self, context, **kwargs):
        return {'data': 'vender driver connected !!!'}
