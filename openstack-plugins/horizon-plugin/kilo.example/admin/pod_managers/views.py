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
from django.utils.datastructures import SortedDict

from horizon import exceptions

from horizon import forms
from horizon import workflows
from horizon import tabs
from horizon import tables
from django import shortcuts
from openstack_dashboard import api

from django.http.response import HttpResponse
from .workflows import AddNewPodManager, EditPodManager
from openstack_dashboard.dashboards.admin.pod_managers import tabs as admin_tabs
from openstack_dashboard.dashboards.admin import pod_managers
from openstack_dashboard.dashboards.admin.pod_managers \
    import tables as admin_tables
from openstack_dashboard.dashboards.admin.instances \
    import tables as project_tables
from openstack_dashboard.dashboards.project.physical_servers import views as project_view
from horizon.utils import memoized
from django.core.urlresolvers import reverse
from .forms import RefreshServerForm, RefreshApprovalServerForm, ManageForm, ConfigForm, EditForm
from openstack_dashboard.dashboards.admin.physical_servers.forms import HypervisorForm


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):

    table_class = admin_tables.AdminPodManagersTable
    #tab_group_class = admin_tabs.PCIeSwitchTabs
    template_name = 'admin/pod_managers/index.html'
    page_title = _("POD Managers")

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        try:
            if 'SELECTED_POD_MANAGER_NAME' not in self.request.session:
                pod_managers_list = api.rsa.pod_managers_list(self.request)
                for pm in pod_managers_list:
                    if str(pm.id) == "1":
                        self.request.session['SELECTED_POD_MANAGER_NAME'] = pm.name
                self.request.session['SELECTED_POD_MANAGER_ID'] = 1
            if self.request.session.has_key('SELECTED_POD_MANAGER_NAME'):
                context["selected_pod_manager"] = self.request.session['SELECTED_POD_MANAGER_NAME']
                try:
                    if 'SELECTED_POD_MANAGER_ID' not in self.request.session:
                        pod_id = 1
                    else:
                        pod_id = self.request.session['SELECTED_POD_MANAGER_ID']
                    pod_manager_hardware_summary = api.rsa.get_pod_manager_hardware_summary(self.request, pod_id)
                    context["pod_manager_hardware_summary"] = pod_manager_hardware_summary
                except Exception:
                    exceptions.handle(self.request,
                                    _('Unable to retrieve get_pod_manager_hardware_summary list.'))
            else:
                self.request.session['SELECTED_POD_MANAGER_ID'] = 0
                pod_id = self.request.session['SELECTED_POD_MANAGER_ID']
                pod_manager_hardware_summary = api.rsa.get_pod_manager_hardware_summary(self.request, pod_id)
                context["pod_manager_hardware_summary"] = pod_manager_hardware_summary
                # context["pod_manager_hardware_summary"] = {}

        except Exception:
            exceptions.handle(self.request,
                            _('Unable to retrieve pod managers statistics.'))

        return context

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

    def has_more_data(self, table):
        return self._more

    def get_data(self):
        '''
        instances = []
        marker = self.request.GET.get(
            project_tables.AdminInstancesTable._meta.pagination_param, None)
        search_opts = self.get_filters({'marker': marker, 'paginate': True})
        # Gather our tenants to correlate against IDs
        try:
            tenants, has_more = api.keystone.tenant_list(self.request)
        except Exception:
            tenants = []
            msg = _('Unable to retrieve instance project information.')
            exceptions.handle(self.request, msg)

        if 'project' in search_opts:
            ten_filter_ids = [t.id for t in tenants
                              if t.name == search_opts['project']]
            del search_opts['project']
            if len(ten_filter_ids) > 0:
                search_opts['tenant_id'] = ten_filter_ids[0]
            else:
                self._more = False
                return []

        try:
            instances, self._more = api.nova.server_list(
                self.request,
                search_opts=search_opts,
                all_tenants=True)
        except Exception:
            self._more = False
            exceptions.handle(self.request,
                              _('Unable to retrieve instance list.'))
        if instances:
            try:
                api.network.servers_update_addresses(self.request, instances,
                                                     all_tenants=True)
            except Exception:
                exceptions.handle(
                    self.request,
                    message=_('Unable to retrieve IP addresses from Neutron.'),
                    ignore=True)

            # Gather our flavors to correlate against IDs
            try:
                flavors = api.nova.flavor_list(self.request)
            except Exception:
                # If fails to retrieve flavor list, creates an empty list.
                flavors = []

            full_flavors = SortedDict([(f.id, f) for f in flavors])
            tenant_dict = SortedDict([(t.id, t) for t in tenants])
            # Loop through instances to get flavor and tenant info.
            for inst in instances:
                flavor_id = inst.flavor["id"]
                try:
                    if flavor_id in full_flavors:
                        inst.full_flavor = full_flavors[flavor_id]
                    else:
                        # If the flavor_id is not in full_flavors list,
                        # gets it via nova api.
                        inst.full_flavor = api.nova.flavor_get(
                            self.request, flavor_id)
                except Exception:
                    msg = _('Unable to retrieve instance size information.')
                    exceptions.handle(self.request, msg)
                tenant = tenant_dict.get(inst.tenant_id, None)
                inst.tenant_name = getattr(tenant, "name", None)
        return instances
        '''
        request = self.request
        pod_managers_to_list = []
        self._more = False
        try:
            pod_managers_to_list = api.rsa.pod_managers_list(request)
        except:
            exceptions.handle(request,
                              _('Unable to retrieve pod managers list.'))
        return pod_managers_to_list



    def get_filters(self, filters):
        filter_field = self.table.get_filter_field()
        filter_action = self.table._meta._filter_action
        if filter_action.is_api_filter(filter_field):
            filter_string = self.table.get_filter_string()
            if filter_field and filter_string:
                filters[filter_field] = filter_string
        return filters


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
    template_name = 'admin/physical_servers/refresh.html'
    modal_header = _("Refresh Inventory")
    form_id = "refresh_inventory_form"
    submit_label = _("Refresh")
    success_url = reverse_lazy('horizon:admin:pod_managers:index')
    submit_url = reverse_lazy('horizon:admin:pod_managers:refresh')
    page_title = _("Refresh Servers Inventroy")

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

class DetailView(project_view.DetailView):
    """server spec view"""
    template_name = 'admin/physical_servers/detail.html'
    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        server = api.ironic.physical_server_get(self.request, kwargs['uuid'])
        context['name']=server.physical_uuid
        context['console_user']=server.console_user
        context['console_passwd']=server.console_passwd
        return context

class CheckView(project_view.CheckView):
    """server deploy status check view"""
    template_name = 'admin/physical_servers/check.html'

class AddNewPodManagerView(workflows.WorkflowView):
    workflow_class = AddNewPodManager

    def get_initial(self):
        initial = super(AddNewPodManagerView, self).get_initial()
        initial['project_id'] = self.request.user.tenant_id
        initial['user_id'] = self.request.user.id
        return initial

class EditPodManagerView(workflows.WorkflowView):
    workflow_class = EditPodManager
    success_url = reverse_lazy("horizon:admin:pod_managers:index")

    def get_context_data(self, **kwargs):
        context = super(EditPodManagerView, self).get_context_data(**kwargs)
        context["pod_manager_id"] = self.kwargs['pod_manager_id']
        return context

    @memoized.memoized_method
    def get_object(self, *args, **kwargs):
        pod_manager_id = self.kwargs['pod_manager_id']
        try:
            pass
            #return api.nova.server_get(self.request, instance_id)
        except Exception:
            pass
            '''
            redirect = reverse("horizon:project:instances:index")
            msg = _('Unable to retrieve instance details.')
            exceptions.handle(self.request, msg, redirect=redirect)
            '''
    def get_initial(self):
        initial = super(EditPodManagerView, self).get_initial()
        initial.update({'pod_manager_id': self.kwargs['pod_manager_id'],
                        'name': getattr(self.get_object(), 'name', '')})
        return initial


