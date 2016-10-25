# Copyright 2015 Lenovo
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

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from openstack_dashboard import api
from openstack_dashboard.dashboards.admin.physical_servers.tables import AdminPhysicalserversTable, \
AdminApprovalListTable, AdminXClarityManagementTable

from openstack_dashboard.dashboards.admin.virtual_disks.tables import EventlogTable

class AdminPhysicalserversTab(tabs.TableTab):
    name = _("Physical Servers")
    slug = "physical_servers"
    #template_name = "horizon/common/_detail_table.html"
    template_name = "admin/physical_servers/_detail_table.html"
    table_classes = (AdminPhysicalserversTable,)
    preload = False

    def get_physicalservers_data(self):
        request = self.request
        physical_servers = []
        try:
            physical_servers = api.ironic.physical_server_list(request)
        except:
            exceptions.handle(request,
                              _('Unable to retrieve physical server list.'))

        return physical_servers

class AdminApprovalListTab(tabs.TableTab):
    name = _("Physical Servers Approval")
    slug = "physical_servers_approval"
    template_name = "horizon/common/_detail_table.html"
    table_classes = (AdminApprovalListTable,)
    preload = False

    def get_approvallist_data(self):
        request = self.request
        approval_list = []
        try:
            approval_list = api.ironic.get_subscribe_list(request)
        except:
            exceptions.handle(request,
                              _('Unable to retrieve approval list.'))

        return approval_list

class AdminXClarityTab(tabs.TableTab):
    name = _("xClarity Administrators")
    slug = "xclarity_administrator_remotecontrol"
    template_name = "horizon/common/_detail_table.html"
    table_classes = (AdminXClarityManagementTable,)
    preload = False

    def get_xclaritymanagement_data(self):
        request = self.request
        xhmc_list = []
        try:
            xhmc_list = api.ironic.get_xclairty_instance_list(request)
        except:
            exceptions.handle(request,
                              _('Unable to retrieve xclarity list.'))

        return xhmc_list

class PhysicalGroupTabs(tabs.TabGroup):
    """physical server tab view, we may try to add more tabs and tables, to make it
    possible for us to manage CIM driver nodes and servers from HP, Dell, etc. in the future"""

    slug = "physical_group_tabs"
    tabs = (AdminPhysicalserversTab, AdminApprovalListTab, AdminXClarityTab)
    sticky = True

class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("admin/virtual_disks/"
                     "_detail_overview.html")

    def get_context_data(self, request):
        return {"virtualdisk": self.tab_group.kwargs['virtualdisk'], "virtual_disk_id": self.tab_group.kwargs['virtual_disk_id']}

class EventlogTab(tabs.TableTab):
    name = _("Event Log")
    slug = "eventlog"
    table_classes = (EventlogTable,)
    template_name = "admin/virtual_disks/_detail_table.html"
    preload = False

    def get_audit_data(self):
        actions = []
        try:
            '''
            actions = api.nova.instance_action_list(
                self.request, self.tab_group.kwargs['instance_id'])
            '''
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve virtual disk action list.'))

        return sorted(actions, reverse=True, key=lambda y: y.start_time)

class VirtualDiskDetailTabs(tabs.TabGroup):
    slug = "virtual_disk_details"
    tabs = (OverviewTab, EventlogTab)
    sticky = True


