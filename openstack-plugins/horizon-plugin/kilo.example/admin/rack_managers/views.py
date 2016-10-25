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
from django.http import JsonResponse
from django.views.generic import TemplateView
from openstack_dashboard import api
from openstack_dashboard.dashboards.project.physical_servers import views
from openstack_dashboard.dashboards.admin import pod_managers

from django.http.response import HttpResponse
from .assign_workflows import AssignPhysicalServersWork, AddPhysicalServersWork, EditPhysicalServersWork
from openstack_dashboard.dashboards.project.physical_servers import forms as project_form
from openstack_dashboard.dashboards.admin.rack_managers import tabs as admin_tabs
from openstack_dashboard.dashboards.admin.rack_managers \
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

    table_class = admin_tables.AdminRackManagersTable
    #tab_group_class = admin_tabs.PCIeSwitchTabs
    template_name = 'admin/rack_managers/index.html'
    page_title = _("Rack Managers")

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
                        self.request.session[
                            'SELECTED_POD_MANAGER_NAME'] = pm.name
                self.request.session['SELECTED_POD_MANAGER_ID'] = 1
            context["selected_pod_manager"] = self.request.session[
                'SELECTED_POD_MANAGER_NAME']
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve racks statistics.'))
        return context

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
        rack_managers_list = []
        self._more = False
        try:
            if 'SELECTED_POD_MANAGER_ID' not in self.request.session:
                pod_id = 1
            else:
                pod_id = self.request.session['SELECTED_POD_MANAGER_ID']
            rack_managers_list = api.rsa.rack_managers_list(request, pod_id)
        except:
            exceptions.handle(request,
                              _('Unable to retrieve drawer list.'))
        return rack_managers_list

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
    success_url = reverse_lazy('horizon:admin:drawers:index')
    submit_url = reverse_lazy('horizon:admin:drawers:refresh')
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
    tab_group_class = admin_tabs.RackManagerDetailTabs
    template_name = 'admin/rack_managers/_detail.html'
    #redirect_url = 'horizon:project:instances:index'
    page_title = _("Rack Manager Details: {{ rack_manager.name }}")

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
        rack_manager_id = self.kwargs['rack_manager_id']
        rack_manager = {}
        try:
            try:
                if 'SELECTED_POD_MANAGER_ID' not in self.request.session:
                    pod_id = 1
                else:
                    pod_id = self.request.session['SELECTED_POD_MANAGER_ID']
                rack_managers_list = api.rsa.rack_managers_list(self.request, pod_id)
                blades = api.rsa.blades_list(self.request, pod_id)
                rack_manager_id_list  = [ d['id'] for d in rack_managers_list ]
                blades_id_list  = [ b['id'] for b in blades ]
            except:
                exceptions.handle(self.request,
                                _('Unable to retrieve rack_manager list.'))
            result = api.rsa.get_rack_manager_by_id(self.request, rack_manager_id)
            rack_manager = result['data']
            if rack_manager.has_key('location'):
                if 'Rack' in eval(rack_manager['location']):
                    rack_manager['rack'] = eval(rack_manager['location'])['Rack']
                if 'ULocation' in eval(rack_manager['location']):
                    rack_manager['location'] = eval(rack_manager['location'])['ULocation']
            if 'Health' in eval(rack_manager['status']):
                rack_manager['status'] = eval(rack_manager['status'])['Health']
            if rack_manager_id_list[-2] == int(rack_manager_id):
                rack_manager['computer_systems'] = [{'name': 'Computer System 1', 'url': '../../../blades/' + str(blades_id_list[0]) + '/detail/' }, \
                                                {'name': 'Computer System 2', 'url': '../../../blades/' + str(blades_id_list[1]) + '/detail/' },
                                                {'name': 'Computer System 3', 'url': '../../../blades/' + str(blades_id_list[2]) + '/detail/' },
                                              ]
            if rack_manager_id_list[-1] == int(rack_manager_id):
                rack_manager['computer_systems'] = [{'name': 'Computer System 4', 'url': '../../../blades/' + str(blades_id_list[-1]) + '/detail/' }]
            if rack_manager.has_key('location') and eval(rack_manager['location']) == {}:
                rack_manager['location'] = ''
        except:
            import traceback
            traceback.print_exc()
            if int(rack_manager_id) == 1:
                return {
                    'name': u'drawer001',
                    'id': '1',
                    'description': 'test001',
                    'model': '8721',
                    'location': '32U',
                    'status': 'normal',
                    'uuid': '1726g21fg21y2t710',
                    'rack': 'rack001'}
            if int(rack_manager_id) == 3:
                return {
                    'name': u'drawer002',
                    'id': '2',
                    'description': 'test002',
                    'model': '8721',
                    'location': '1U',
                    'status': 'normal',
                    'uuid': '1726g21fg21y1th12',
                    'rack': 'rack001'}
            if int(rack_manager_id) == 5:
                return {
                    'name': u'drawer005',
                    'id': '5',
                    'description': 'test005',
                    'model': '8721',
                    'location': '11U',
                    'status': 'normal',
                    'uuid': '1726g010g01y1th12',
                    'rack': 'rack006'}
            if int(rack_manager_id) == 2:
                return {
                    'name': u'drawer002',
                    'id': '2',
                    'description': 'test002',
                    'model': '8721',
                    'location': '1U',
                    'status': 'normal',
                    'uuid': '1726g21fg21y1th12',
                    'rack': 'rack001'}
            if int(rack_manager_id) == 4:
                return {
                    'name': u'drawer004',
                    'id': '4',
                    'description': 'test004',
                    'model': '8721',
                    'location': '19U',
                    'status': 'normal',
                    'uuid': '1726g11fg21y1th12',
                    'rack': 'rack003'}
        return rack_manager

    def get_tabs(self, request, *args, **kwargs):
        rack_manager = self.get_data()
        return self.tab_group_class(request, rack_manager=rack_manager, **kwargs)


class CheckView(project_view.CheckView):
    """server deploy status check view"""
    template_name = 'admin/physical_servers/check.html'


class GetOneDrawerInfoView(TemplateView):

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
        drawer_id = context["drawer_id"]
        print(drawer_id)
        if int(drawer_id) == 1:
            context['drawer_info'] = {
                'manufacturer': 'IBM',
                'indicatorled': 'testled',
                'SKU': '920000035'}
        if int(drawer_id) == 10:
            context['drawer_info'] = {
                'manufacturer': 'Lenovo',
                'indicatorled': 'testled',
                'SKU': '920000035'}
        if int(drawer_id) == 5:
            context['drawer_info'] = {
                'manufacturer': 'cisco',
                'indicatorled': 'testled',
                'SKU': '920000035'}
        if int(drawer_id) == 2:
            context['drawer_info'] = {
                'manufacturer': 'Adobe',
                'indicatorled': 'testled',
                'SKU': '920000035'}
        if int(drawer_id) == 4:
            context['drawer_info'] = {
                'manufacturer': 'VMware',
                'indicatorled': 'testled',
                'SKU': '920000035'}
        context.pop("view", None)
        return context

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)
