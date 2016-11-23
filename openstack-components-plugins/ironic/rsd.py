# -*- encoding: utf-8 -*-
#
# Copyright 2013 Hewlett-Packard Development Company, L.P.
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
"""
RSD Driver
"""

from ironic.drivers import base
from ironic.drivers.modules import inspector
from ironic.drivers.modules import rsd_tool
from ironic.drivers.modules import iscsi_deploy
from ironic.drivers.modules import pxe
from ironic.drivers import utils


class PXEAndRSCDriver(base.BaseDriver):
    def __init__(self):
        self.power = rsd_tool.RSCPower()
        self.boot = pxe.PXEBoot()
        self.deploy = iscsi_deploy.ISCSIDeploy()
        self.management = rsd_tool.RSCManagement()
        self.inspect = inspector.Inspector.create_if_enabled(
            'PXEAndRSCDriver')
        self.iscsi_vendor = iscsi_deploy.VendorPassthru()
        self.mapping = {'heartbeat': self.iscsi_vendor,
                        'pass_deploy_info': self.iscsi_vendor,
                        'pass_bootloader_install_info': self.iscsi_vendor}
        self.driver_passthru_mapping = {'lookup': self.iscsi_vendor}
        self.vendor = utils.MixinVendorInterface(
            self.mapping,
            driver_passthru_mapping=self.driver_passthru_mapping)


