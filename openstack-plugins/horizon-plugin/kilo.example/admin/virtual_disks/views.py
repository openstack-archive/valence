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

import logging

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions

from horizon import forms
from horizon import workflows
from horizon import tabs
from horizon import tables
from django import shortcuts
from django.http import JsonResponse
from django.views.generic import TemplateView
from openstack_dashboard import api
from openstack_dashboard.dashboards.project.physical_servers import views
from openstack_dashboard.dashboards.admin import pod_managers

from django.http.response import HttpResponse
from .assign_workflows import AssignPhysicalServersWork, AddPhysicalServersWork, EditPhysicalServersWork
from openstack_dashboard.dashboards.project.physical_servers import forms as project_form
from openstack_dashboard.dashboards.admin.virtual_disks import tabs as admin_tabs
from openstack_dashboard.dashboards.project.physical_servers import views as project_view
from openstack_dashboard.dashboards.admin.virtual_disks \
    import tables as admin_tables
from horizon.utils import memoized
from django.core.urlresolvers import reverse
from .forms import RefreshServerForm, RefreshApprovalServerForm, ManageForm, ConfigForm, EditForm
from openstack_dashboard.dashboards.admin.physical_servers.forms import HypervisorForm


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    #tab_group_class = admin_tabs.PhysicalGroupTabs
    table_class = admin_tables.AdminVirtualDisksTable
    template_name = 'admin/virtual_disks/index.html'
    page_title = _("Virtual Disks")
    '''
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        try:
            context["stats"] = api.ironic.physical_servers_stats(self.request)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve physical servers statistics.'))

        return context
    '''
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        try:
            if 'SELECTED_POD_MANAGER_NAME' not in self.request.session:
                pod_managers_list = api.rsa.pod_managers_list(self.request)
                for pm in pod_managers_list:
                    if str(pm.id) == "1":
                        self.request.session['SELECTED_POD_MANAGER_NAME'] = pm.name
                self.request.session['SELECTED_POD_MANAGER_ID'] = 1
            context["selected_pod_manager"] = self.request.session['SELECTED_POD_MANAGER_NAME']
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve composed servers statistics.'))
        try:
            if 'SELECTED_POD_MANAGER_ID' not in self.request.session:
                pod_id = 1
            else:
                pod_id = self.request.session['SELECTED_POD_MANAGER_ID']
            storage_table_name, storage_list = api.rsa.storage_list(self.request, pod_id=pod_id)
            for i, s in enumerate(storage_list):
                if 'status' in s.keys():
                    status_tmp = eval(s['status'])
                    if 'State' in status_tmp:
                        storage_list[i]['State'] = status_tmp['State']
                    if 'Health' in status_tmp:
                        storage_list[i]['Health'] = status_tmp['Health']
            context["storage_table_name"] = storage_table_name
            context["storage_list"] = storage_list
        except:
            exceptions.handle(self.request,
                              _('Unable to retrieve storage list.'))

        return context

    def has_more_data(self, table):
        return self._more

    def get_data(self):
        request = self.request
        virtualdisk_list = []
        self._more = False
        try:
            if 'SELECTED_POD_MANAGER_ID' not in self.request.session:
                pod_id = 1
            else:
                pod_id = self.request.session['SELECTED_POD_MANAGER_ID']
            virtualdisk_list = api.rsa.virtualdisks_list(request, pod_id=pod_id)
        except:
            exceptions.handle(request,
                              _('Unable to retrieve virtual disk list.'))
        return virtualdisk_list

    def get_filters(self, filters):
        filter_field = self.table.get_filter_field()
        filter_action = self.table._meta._filter_action
        if filter_action.is_api_filter(filter_field):
            filter_string = self.table.get_filter_string()
            if filter_field and filter_string:
                filters[filter_field] = filter_string
        return filters

class DeployView(views.DeployView):
    """deploy view of Admin side, currently admin and project users have the same deploy view"""

    template_name = 'admin/physical_servers/deploy.html'
    form_class = project_form.DeployPhysicalServerForm
    success_url = reverse_lazy('horizon:admin:physical_servers:index')
    submit_url = "horizon:admin:physical_servers:deploy"

    def get_initial(self):
        server = self.get_object()
        return {'uuid': self.kwargs['uuid'],
                'physical_uuid': server.physical_uuid,
                'macs': server.mac_addresses,
                }

class AssociateAuthView(views.AssociateAuthView):
    """deploy view of Admin side, currently admin and project users have the same deploy view"""

    template_name = 'admin/physical_servers/associate.html'
    form_class = project_form.AssociatePhysicalServerForm
    success_url = reverse_lazy('horizon:admin:physical_servers:index')
    submit_url = "horizon:admin:physical_servers:associate_auth"

class HypervisorView(forms.ModalFormView):
    """Extract hypervisor/host list from nova and associate with physical server"""

    form_class = HypervisorForm
    template_name = 'admin/physical_servers/hypervisor.html'
    modal_header = _("Associate Hypervisor")
    form_id = "associate_hypervisor_modal"
    submit_label = _("Associate")
    success_url = reverse_lazy('horizon:admin:physical_servers:index')
    submit_url = 'horizon:admin:physical_servers:hypervizor'
    page_title = _("Associate server with nova hypervisor host")

    def get_context_data(self, **kwargs):
        context = super(HypervisorView, self).get_context_data(**kwargs)
        return context

class RefreshView(forms.ModalFormView):

    form_class = RefreshServerForm
    template_name = 'admin/rsa_servers/refresh.html'
    modal_header = _("Refresh Inventory")
    form_id = "refresh_inventory_form"
    submit_label = _("Refresh")
    success_url = reverse_lazy('horizon:admin:virtual_disks:index')
    submit_url = reverse_lazy('horizon:admin:virtual_disks:refresh')
    page_title = _("Refresh Virtual Disks Inventroy")

    def get_context_data(self, **kwargs):
        context = super(RefreshView, self).get_context_data(**kwargs)
        return context


class RefreshApprovalView(forms.ModalFormView):
    """click refresh button to pull approval list from DB to show"""

    form_class = RefreshApprovalServerForm
    template_name = 'admin/physical_servers/refresh_approval.html'
    modal_header = _("Refresh Approval List")
    form_id = "refresh_approval_modal"
    submit_label = _("Refresh")
    success_url = reverse_lazy('horizon:admin:physical_servers:index')
    submit_url = reverse_lazy('horizon:admin:physical_servers:refresh_approval')
    page_title = _("Refresh Approval List")

    def get_context_data(self, **kwargs):
        context = super(RefreshApprovalView, self).get_context_data(**kwargs)
        return context


class AssignsView(workflows.WorkflowView):
    """Assign work flow view, only Admin side can do assign"""

    workflow_class = AssignPhysicalServersWork

class AddView(workflows.WorkflowView):
    """Assign work flow view, only Admin side can do assign"""

    workflow_class = AddPhysicalServersWork

class EditView(workflows.WorkflowView):
    """Assign work flow view, only Admin side can do assign"""

    workflow_class = EditPhysicalServersWork

    def get_initial(self):
        initial = super(EditView, self).get_initial()

        server_id = self.kwargs['uuid']
        initial['server_uuid'] = server_id
        server = api.ironic.physical_server_get(self.request, server_id)
        initial['ip_address'] = server.management_ip
        initial['user'] = server.console_user
        initial['password'] = server.console_passwd
        initial['port'] = server.console_port
        initial['server_name'] = server.name
        initial['vendor_name'] = server.vendor_name
        initial['model'] = server.product_name
        initial['cpu_number'] = server.cpu
        initial['memory_size'] = server.memory
        initial['disk_size'] = server.disk

        return initial


class ManageView(forms.ModalFormView):
    """the manage xClarity view"""

    form_class = ManageForm
    template_name = 'admin/physical_servers/manage.html'
    modal_header = _("Manage XClarity")
    form_id = "manage_xclarity_modal"
    submit_label = _("Manage")
    success_url = reverse_lazy('horizon:admin:physical_servers:index')
    submit_url = reverse_lazy('horizon:admin:physical_servers:manage')
    page_title = _("Manage XClarity")

    def get_context_data(self, **kwargs):
        context = super(ManageView, self).get_context_data(**kwargs)
        return context

class EditXClarityView(forms.ModalFormView):
    """the edit xClarity view, the same form as manage, but with initial value"""

    form_class = EditForm
    template_name = 'admin/physical_servers/editxclarity.html'
    modal_header = _("Edit XClarity")
    form_id = "edit_xclarity_modal"
    submit_label = _("Edit")
    success_url = reverse_lazy('horizon:admin:physical_servers:index')
    submit_url = 'horizon:admin:physical_servers:edit_xclarity'
    page_title = _("Edit XClarity")

    def get_context_data(self, **kwargs):
        context = super(EditXClarityView, self).get_context_data(**kwargs)
        args = (self.kwargs['id'],)
        context["id"] = self.kwargs['id']
        context["submit_url"] = reverse(self.submit_url, args=args)

        return context

    @memoized.memoized_method
    def get_object(self):
        """
        by default, self.kwargs['xxx'], here xxx means the url Pattern ?P<uuid> or ?P<server_id>
        in physical server, we use ?P<uuid>, so kwargs['uuid']=row key
        """
        try:
            return api.ironic.get_xclarity(self.request, self.kwargs['id'])
        except Exception:
            msg = _('Unable to retrieve XClarity.')
            url = reverse('horizon:admin:physical_servers:index')
            exceptions.handle(self.request, msg, redirect=url)

    def get_initial(self):
        xclarity_inst = self.get_object()
        return {'xclarity_id': self.kwargs['id'],
                'xclarity_ip': xclarity_inst.ipaddress,
                'xclarity_user': xclarity_inst.username,
                'xclarity_passwd': xclarity_inst.password,
                }

class ConfigView(forms.ModalFormView):
    """the manage xClarity view"""

    form_class = ConfigForm
    template_name = 'admin/physical_servers/config.html'
    modal_header = _("Configure XClarity")
    form_id = "config_xclarity_modal"
    submit_label = _("Confirm")
    success_url = reverse_lazy('horizon:admin:physical_servers:index')
    submit_url = reverse_lazy('horizon:admin:physical_servers:config')
    page_title = _("Configure XClarity")

    def get_context_data(self, **kwargs):
        context = super(ConfigView, self).get_context_data(**kwargs)
        return context

class DetailView(tabs.TabView):
    tab_group_class = admin_tabs.VirtualDiskDetailTabs
    template_name = 'admin/virtual_disks/_detail.html'
    #redirect_url = 'horizon:project:instances:index'
    page_title = _("Virtual Disk Details: {{ virtualdisk.name }}")

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        #instance = self.get_data()
        #context["virtualdisk"] = virtualdisk
        #table = project_tables.InstancesTable(self.request)
        #context["url"] = reverse(self.redirect_url)
        #context["actions"] = table.render_row_actions(instance)
        return context

    @memoized.memoized_method
    def get_data(self):
        virtual_disk_id = self.kwargs['virtual_disk_id']
        try:
            if 'SELECTED_POD_MANAGER_ID' not in self.request.session:
                pod_id = 1
            else:
                pod_id = self.request.session['SELECTED_POD_MANAGER_ID']
            virtualdisk = api.rsa.get_virtual_disk_by_id(self.request, pod_id, virtual_disk_id)
        except:
            virtualdisk = {}
            if int(virtual_disk_id) == 1:
                return {'image': 'ubuntu', 'targets': 'monkey', 'snapshot':'xx920000035', 'physical_driver':'HD9289, HD9283', 'master_driver': 'HD9289', 'events': 'nothing new', 'name': 'VD001', 'status':'normal', 'health':'normal', 'type':'x500', 'mode':'active', 'capacity': '100T', 'rack': 'rack006'}
            if int(virtual_disk_id) == 2:
                return {'image': 'Freebsd', 'targets': 'Spiderman', 'snapshot':'ww920000035', 'physical_driver':'HD9289', 'master_driver': 'HD9289', 'events': 'nothing new', 'name': 'VD002', 'status':'normal', 'health':'normal', 'type':'x500', 'mode':'active', 'capacity': '100T', 'rack': 'rack001'}
            if int(virtual_disk_id) == 3:
                return {'image': 'centos', 'targets': 'banana', 'snapshot':'ss20000036', 'physical_driver':'HD9289', 'master_driver': 'HD9289', 'events': 'nothing new', 'name': 'VD003', 'status':'normal', 'health':'normal', 'type':'x500', 'mode':'active', 'capacity': '100T', 'rack': 'rack001'}
            if int(virtual_disk_id) == 4:
                return {'image': 'Windows_server', 'Antman': 'testled', 'snapshot':'kk9200232', 'physical_driver':'HD9289', 'master_driver': 'HD9289', 'events': 'nothing new', 'name': 'VD004', 'status':'normal', 'health':'normal', 'type':'x500', 'mode':'active', 'capacity': '100T', 'rack': 'rack006'}
            if int(virtual_disk_id) == 5:
                return {'image': 'Fedora', 'targets': 'jungle', 'snapshot':'dd920000035', 'physical_driver':'HD9289', 'master_driver': 'HD9289', 'events': 'nothing new', 'name': 'VD005', 'status':'normal', 'health':'normal', 'type':'x500', 'mode':'active', 'capacity': '100T', 'rack': 'rack006'}
        return virtualdisk['data']

    def get_tabs(self, request, *args, **kwargs):
        virtualdisk = self.get_data()
        return self.tab_group_class(request, virtualdisk=virtualdisk, **kwargs)

class CheckView(project_view.CheckView):
    """server deploy status check view"""
    template_name = 'admin/physical_servers/check.html'

class GetOneVirtualDiskInfoView(TemplateView):
    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        virtual_disk_id = context["virtual_disk_id"]
        print(virtual_disk_id)
        if int(virtual_disk_id) == 1:
            context['virtualdisk_info'] = {'image': 'ubuntu', 'targets': 'monkey', 'snapshot':'xx920000035', 'physical_driver':'HD9289,HD231', 'master_driver': 'HD9289', 'events': 'nothing new'}
        if int(virtual_disk_id) == 3:
            context['virtualdisk_info'] = {'image': 'centos', 'targets': 'banana', 'snapshot':'ss20000036', 'physical_driver':'HD9289', 'master_driver': 'HD9289', 'events': 'nothing new'}
        if int(virtual_disk_id) == 5:
            context['virtualdisk_info'] = {'image': 'Fedora', 'targets': 'jungle', 'snapshot':'dd920000035', 'physical_driver':'HD9289', 'master_driver': 'HD9289', 'events': 'nothing new'}
        if int(virtual_disk_id) == 2:
            context['virtualdisk_info'] = {'image': 'Freebsd', 'targets': 'Spiderman', 'snapshot':'ww920000035', 'physical_driver':'HD9289', 'master_driver': 'HD9289', 'events': 'nothing new'}
        if int(virtual_disk_id) == 4:
            context['virtualdisk_info'] = {'image': 'Windows_server', 'Antman': 'testled', 'snapshot':'kk9200232', 'physical_driver':'HD9289', 'master_driver': 'HD9289', 'events': 'nothing new'}
        context.pop("view", None)
        return context

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)
