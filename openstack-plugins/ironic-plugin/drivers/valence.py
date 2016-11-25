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


from ironic.drivers import base
from ironic.drivers.modules.valence import power
from ironic.drivers.modules.valence import management
from ironic.drivers.modules.valence import vendor

from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class ValenceDriver(base.BaseDriver):
    """valence driver instalce"""

    def __init__(self):
        self.power = power.ValencePower()
        self.management = management.ValenceManagement()
        self.vendor = vendor.ValenceVendor()
