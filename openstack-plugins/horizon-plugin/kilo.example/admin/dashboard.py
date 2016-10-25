# Copyright 2012 Nebula, Inc.
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

from django.utils.translation import ugettext_lazy as _

import horizon


class SystemPanels(horizon.PanelGroup):
    slug = "admin"
    name = _("System")
    panels = ('overview', 'physical_servers', 'metering', 'hypervisors', 'aggregates',
              'instances', 'volumes', 'flavors', 'images',
              'networks', 'routers', 'defaults', 'metadata_defs', 'info')

class RSAPanels(horizon.PanelGroup):
    slug = "rsd"
    name = _("RSD")
    panels = ('pod_managers','rsa_servers', 'virtual_disks', 'racks', 'rack_managers', 'ethernet_switches', 'drawers', 'blades', 'events')
    #panels = ('pod_managers','rsa_servers', 'virtual_disks', 'racks', 'rack_managers', 'ethernet_switches', 'drawers',  'pcie_switches', 'blades', 'events')

class Admin(horizon.Dashboard):
    name = _("Admin")
    slug = "admin"
    panels = (RSAPanels, SystemPanels,)
    default_panel = 'overview'
    permissions = ('openstack.roles.admin',)


horizon.register(Admin)
