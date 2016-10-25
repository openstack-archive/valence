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
from django import shortcuts
from openstack_dashboard import api
from openstack_dashboard.dashboards.project.physical_servers import views

from django.http.response import HttpResponse
from .assign_workflows import AssignPhysicalServersWork, AddPhysicalServersWork, EditPhysicalServersWork
from openstack_dashboard.dashboards.project.physical_servers import forms as project_form
from openstack_dashboard.dashboards.admin.physical_servers import tabs as admin_tabs
from openstack_dashboard.dashboards.project.physical_servers import views as project_view
from horizon.utils import memoized
from django.core.urlresolvers import reverse
from .forms import RefreshServerForm, RefreshApprovalServerForm, ManageForm, ConfigForm, EditForm
from openstack_dashboard.dashboards.admin.physical_servers.forms import HypervisorForm


LOG = logging.getLogger(__name__)


class IndexView(tabs.TabbedTableView):
    """index view of the physical server tabbed view"""
    
    tab_group_class = admin_tabs.PhysicalGroupTabs
    template_name = 'admin/physical_servers/index.html'
    page_title = _("Physical Servers")
    
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        try:
            context["stats"] = api.ironic.physical_servers_stats(self.request)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve physical servers statistics.'))

        return context
    

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
    """Click refresh button to pull data from xClarity to ironic DB and horizon"""
    
    form_class = RefreshServerForm
    template_name = 'admin/physical_servers/refresh.html'
    modal_header = _("Refresh Inventory")
    form_id = "refresh_inventory_form"
    submit_label = _("Refresh")
    success_url = reverse_lazy('horizon:admin:physical_servers:index')
    submit_url = reverse_lazy('horizon:admin:physical_servers:refresh')
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
