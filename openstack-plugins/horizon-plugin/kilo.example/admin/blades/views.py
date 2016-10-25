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
from openstack_dashboard import api
from openstack_dashboard.dashboards.admin import pod_managers

#from django.http.response import HttpResponse
from openstack_dashboard.dashboards.admin.blades \
    import tables as admin_tables
from openstack_dashboard.dashboards.project.physical_servers import forms as project_form
from openstack_dashboard.dashboards.admin.blades import tabs as admin_tabs
from horizon.utils import memoized
from django.core.urlresolvers import reverse
from .forms import RefreshServerForm


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):

    table_class = admin_tables.AdminBladeTable
    #tab_group_class = admin_tabs.PCIeSwitchTabs
    template_name = 'admin/blades/index.html'
    page_title = _("Computer systems")

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
        blades = []
        self._more = False
        try:
            if 'SELECTED_POD_MANAGER_ID' not in self.request.session:
                pod_id = 1
            else:
                pod_id = self.request.session['SELECTED_POD_MANAGER_ID']
            blades = api.rsa.blades_list(request, pod_id)
        except:
            exceptions.handle(request,
                              _('Unable to retrieve physical server list.'))
        return blades

    def get_filters(self, filters):
        filter_field = self.table.get_filter_field()
        filter_action = self.table._meta._filter_action
        if filter_action.is_api_filter(filter_field):
            filter_string = self.table.get_filter_string()
            if filter_field and filter_string:
                filters[filter_field] = filter_string
        return filters


class DetailView(tabs.TabView):
    tab_group_class = admin_tabs.BladeDetailTabs
    template_name = 'admin/blades/_detail.html'
    #redirect_url = 'horizon:project:instances:index'
    page_title = _("Computer System Details: {{ blade.name }}")

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
        blade_id = self.kwargs['blade_id']
        if 'SELECTED_POD_MANAGER_ID' not in self.request.session:
            pod_id = 1
        else:
            pod_id = self.request.session['SELECTED_POD_MANAGER_ID']
        blade = {}
        try:
            blade = api.rsa.get_computer_system_by_id(
                self.request, pod_id, blade_id)
            if 'Health' in eval(blade['data']['status']):
                blade['data']['status'] = eval(blade['data']['status'])['Health']
            try:
                if 'Rack' in eval(blade['data']['location']):
                    blade['rack'] = eval(blade['data']['location'])['Rack']
                    blade['data']['rack'] = eval(blade['data']['location'])['Rack']
                if 'ULocation' in eval(blade['data']['location']):
                    blade['location'] = eval(blade['data']['location'])['ULocation']
                    blade['data']['location'] = eval(blade['data']['location'])['ULocation']
            except:
                pass
        except:
            import traceback
            traceback.print_exc()
            if int(blade_id) == 1:
                return {
                    'name': 'Computer system 001',
                    'status': 'normal',
                    'model': 'sx200',
                    'rack': 'rack003',
                    'location': '2U',
                    'manufacturer': 'lenovo',
                    'manufacturingdate': '2014-12-21',
                    'serialnumber': 'xx920000035',
                    'firmwareversion': '9.0',
                    'role': 'master',
                    'port_usage': '7/24',
                    'partnumber': 'pt0920001',
                    'firmwarename': 'hyperxx0520',
                    'events': 'your mama and daddy get married'}
            if int(blade_id) == 2:
                return {
                    'name': 'Computer system 002',
                    'status': 'normal',
                    'model': 'sx200',
                    'rack': 'rack003',
                    'location': '3U',
                    'manufacturer': 'ibm',
                    'manufacturingdate': '2014-12-21',
                    'serialnumber': 'ss20000036',
                    'firmwareversion': '9.0',
                    'role': 'master',
                    'port_usage': '7/24',
                    'partnumber': 'pt0928371',
                    'firmwarename': 'hyperxx0520',
                    'events': 'your mama and daddy get married'}
            if int(blade_id) == 3:
                return {
                    'name': 'Computer system 003',
                    'status': 'normal',
                    'model': 'sx200',
                    'rack': 'rack003',
                    'location': '5U',
                    'manufacturer': 'redhat',
                    'manufacturingdate': '2014-12-21',
                    'serialnumber': 'dd920000035',
                    'firmwareversion': '9.0',
                    'role': 'master',
                    'port_usage': '7/24',
                    'partnumber': 'pt0928371',
                    'firmwarename': 'hyperxx0520',
                    'events': 'your mama and daddy get married'}
            if int(blade_id) == 4:
                return {
                    'name': 'Computer system 004',
                    'status': 'normal',
                    'model': 'sx200',
                    'rack': 'rack006',
                    'location': '8U',
                    'manufacturer': 'Canonical',
                    'manufacturingdate': '2014-12-21',
                    'serialnumber': 'ww920000035',
                    'firmwareversion': '9.0',
                    'role': 'master',
                    'port_usage': '7/24',
                    'partnumber': 'pt0928371',
                    'firmwarename': 'hyperxx0520',
                    'events': 'your mama and daddy get married'}
            if int(blade_id) == 5:
                return {
                    'name': 'Computer system 005',
                    'status': 'normal',
                    'model': 'sx200',
                    'rack': 'rack006',
                    'location': '6U',
                    'manufacturer': 'Huaiwei',
                    'manufacturingdate': '2014-12-21',
                    'serialnumber': 'kk9200232',
                    'firmwareversion': '9.0',
                    'role': 'master',
                    'port_usage': '7/24',
                    'partnumber': 'pt0928371',
                    'firmwarename': 'hyperxx0520',
                    'events': 'your mama and daddy get married'}
            if int(blade_id) == 6:
                return {
                    'name': 'Computer system 006',
                    'status': 'normal',
                    'model': 'sx200',
                    'rack': 'rack003',
                    'location': '12U',
                    'manufacturer': 'Cisco',
                    'manufacturingdate': '2014-12-21',
                    'serialnumber': 'kk9200232',
                    'firmwareversion': '9.0',
                    'role': 'master',
                    'port_usage': '7/24',
                    'partnumber': 'pt0928371',
                    'firmwarename': 'hyperxx0520',
                    'events': 'your mama and daddy get married'}
            if int(blade_id) == 7:
                return {
                    'name': 'Computer system 007',
                    'status': 'normal',
                    'model': 'sx200',
                    'rack': 'rack003',
                    'location': '11U',
                    'manufacturer': 'Ubuntu',
                    'manufacturingdate': '2014-12-21',
                    'serialnumber': 'kk9200232',
                    'firmwareversion': '9.0',
                    'role': 'master',
                    'port_usage': '7/24',
                    'partnumber': 'pt0987237',
                    'firmwarename': 'hyperxx0520',
                    'events': 'your mama and daddy get married'}
        return blade['data']

    def get_tabs(self, request, *args, **kwargs):
        blade = self.get_data()
        return self.tab_group_class(request, blade=blade, **kwargs)


class RefreshView(forms.ModalFormView):

    form_class = RefreshServerForm
    template_name = 'admin/rsa_servers/refresh.html'
    modal_header = _("Refresh Inventory")
    form_id = "refresh_inventory_form"
    submit_label = _("Refresh")
    success_url = reverse_lazy('horizon:admin:blades:index')
    submit_url = reverse_lazy('horizon:admin:blades:refresh')
    page_title = _("Refresh Computer System Inventroy")

    def get_context_data(self, **kwargs):
        context = super(RefreshView, self).get_context_data(**kwargs)
        return context
