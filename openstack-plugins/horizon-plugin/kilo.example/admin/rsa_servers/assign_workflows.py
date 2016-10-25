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

from horizon import workflows
from horizon import forms
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import messages
from django.core.urlresolvers import reverse
from horizon.utils import validators
from openstack_dashboard import api
# from cinder.tests.api.contrib.test_scheduler_hints import UUID

class SelectServerAction(workflows.Action):
    """Admin side assign servers to tenant work flow, select the servers"""
  
    assign_number = forms.ChoiceField(label=_('Randomly Assign server number'),
                                    help_text=_("Select a number between 1-5."),
                                    choices=[(0,'0'),(1,'1'),(2,'2'),(3,'3'),(4,'4'),(5,'5'),],
                                    widget=forms.Select(attrs={
                                        'class': 'switchable switched',                                        
                                        }),
                                    required=True)
       
    specified_servers = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5,                                                                     
                                     }),
        label=_("Specified Servers if you want"),
        help_text=_("Specified the physical servers to assign. Each entry is: "
                    "the ip address of IMM with the server"
                    "(e.g., 10.240.212.100) "
                    "and one entry per line."),
        required=False)
 
     
 
    def __init__(self, request,  context, *args, **kwargs):
        super(SelectServerAction, self).__init__(request, context, *args, **kwargs)  
       
 
    class Meta(object):
        name = _("Physical Servers")
        help_text = _("Assign physical servers. "
                      "select physical server numbers or specified some servers through IMM ip address."
                      "The total assign numbers will be the randomly assigned plus specified servers")
 
    def clean(self):
        cleaned_data = super(SelectServerAction, self).clean()        
        return cleaned_data
     
class SelectServerInfo(workflows.Step):
    action_class = SelectServerAction
    contributes = ("assign_number", "specified_servers")
 
 
 
class SelectTenantAction(workflows.Action):
    """Admin side assign servers to tenant work flow, select the tenant"""
 
    select_tenant = forms.ChoiceField(label=_('Tenant'),
                                    help_text=_("Select a Tenant to assign servers."),
                                    choices=[],
                                    widget=forms.Select(attrs={
                                        'class': 'switchable switched',
                                        }),
                                    required=True)        
     
 
    def __init__(self, request,  context, *args, **kwargs):
        super(SelectTenantAction, self).__init__(request, context, *args, **kwargs)  
        all_projects, has_more = api.keystone.tenant_list(request)

        project_list=[]
        project_list.append(('',_('Select Tenant')))
        for project in all_projects:
            project_list.append((project.id, project.name))            
        self.fields['select_tenant'].choices = project_list
    
 
    class Meta(object):
        name = _("Tenant")
        help_text = _("Assign physical servers. "
                      "Choose the tenant which will be assigned physical servers.")
 
    def clean(self):
        cleaned_data = super(SelectTenantAction, self).clean()        
        return cleaned_data
     
class SelectTenantInfo(workflows.Step):
    action_class = SelectTenantAction
    contributes = ("select_tenant",)
 
     
 
class AssignPhysicalServersWork(workflows.Workflow):
    slug = "assign"
    name = _("Assign Physical Servers")
    finalize_button_name = _("Assign")
    success_message = _('Assign physical servers successfully.')
    failure_message = _('Unable to assign physical servers.')

    default_steps = (SelectServerInfo,
                     SelectTenantInfo)
    wizard = True
  
    def get_success_url(self):
        return reverse("horizon:admin:physical_servers:index")
 
    def get_failure_url(self):
        return reverse("horizon:admin:physical_servers:index")
 
    def format_status_message(self, message):
        """if the message has format, we can make it in detail way"""
        return message 
 
    def handle(self, request, data):
        
        assign_number = int(data['assign_number'])        
        select_tenant = data['select_tenant']                        
        select_servers = data['specified_servers']
        
        
        servers=[]
        msg=_('At least one server should be assigned')
        if select_servers!='':
            serversplits=select_servers.split('\r\n')
            for server in serversplits:
                if server!='':
                    servers.append(server.strip())
        
        try:
            if servers or assign_number !=0:
                select_name=''
                all_projects, has_more = api.keystone.tenant_list(request)
                for project in all_projects:
                    if project.id==select_tenant:
                        select_name = project.name 
                        break

                filter_items={}
                filter_items['assign_number'] = assign_number
                filter_items['fixed_servers'] = servers
                filter_items['target_tenant'] = select_tenant
                filter_items['target_tenant_name'] = select_name
                filter_items['direction'] = 'admin'
                res = api.ironic.assign_servers(request, **filter_items)
                if res != 'Assigned successfully':
                    msg=_('operation failed, please check if enough servers in resource pool met the requirement')
                    messages.error(request, msg)
                    return False 
            else:
                messages.error(request, msg)
                return False 
        except:
            msg=_('operation failed')
            messages.error(request, msg)
            exceptions.handle(request, msg)
            return False                
        return True


 

class FillBasicAction(workflows.Action):
    """add pxe_ipminative info"""
  
    server_name = forms.CharField(max_length="255",
                                label=_("Server Name"),
                                help_text=_("The name of the phsical server."),
                                required=True)
    
    vendor_name = forms.ChoiceField(
        label=_("Vendor name"),
        help_text=_("vendor name of the physical servers"),
        choices=[('', _('Select Vendor')),
                 ('HP',_('HP')),
                 ('Dell',_('Dell')),
                 ('IBM',_('IBM')),
                 ('Lenovo',_('Lenovo')),                                          
                 ],
        required=True,
        widget=forms.Select(attrs={'class':'switchable'})
    )
    
    model = forms.CharField(max_length="255",
                        label=_("Modle"),
                        help_text=_("product name"),
                        required=False
                        )    
     
    def __init__(self, request,  context, *args, **kwargs):
        super(FillBasicAction, self).__init__(request, context, *args, **kwargs)  
        self.fields['server_name'].initial = self.initial.get("server_name", '')
        self.fields['vendor_name'].initial = self.initial.get("vendor_name", '')
        self.fields['model'].initial = self.initial.get("model", '')

 
    class Meta(object):
        name = _("Basic Info")
        help_text = _("Basic info of the physical servers")
 
    def clean(self):
        cleaned_data = super(FillBasicAction, self).clean()        
        return cleaned_data
     
class FillBasicInfo(workflows.Step):
    action_class = FillBasicAction
    contributes = ("server_name", "vendor_name", "model")


class FillManagementAction(workflows.Action):
    """add pxe_ipminative info"""
  
    ip_address = forms.CharField(max_length="255",
                                label=_("Management Address"),
                                help_text=_("The IP address of IPMI Manager."),
                                required=True)
    user = forms.CharField(max_length="255",
                                label=_("Management User"),
                                help_text=_("User name of IPMI Manager."),
                                required=True)
    password = forms.RegexField(
        label=_("Management Password"),
        widget=forms.PasswordInput(render_value=True),
        help_text=_("Password of IPMI Manager."),
        regex=validators.password_validator(),
        error_messages={'invalid': validators.password_validator_msg()})
    
    port = forms.CharField(max_length="255",
                        label=_("Terminal Port"),
                        help_text=_("IPMI terminal port."),
                        required=False
                        ) 
 
     
 
    def __init__(self, request,  context, *args, **kwargs):
        super(FillManagementAction, self).__init__(request, context, *args, **kwargs)  
        self.fields['ip_address'].initial = self.initial.get("ipmi_address", '')
        self.fields['user'].initial = self.initial.get("ipmi_username", '')
        self.fields['password'].initial = self.initial.get("ipmi_password", '')
        self.fields['port'].initial = self.initial.get("ipmi_terminal_port", '')
 
    class Meta(object):
        name = _("Management Info")
        help_text = _("add ipmi authentication info of node")
 
    def clean(self):
        cleaned_data = super(FillManagementAction, self).clean()        
        return cleaned_data
     
class FillManagementInfo(workflows.Step):
    action_class = FillManagementAction
    contributes = ("ip_address", "user", "password", "port")
    
class FillExtraAction(workflows.Action):
    """we may have more detailed info, such as cpu frequency, memory number, disk type etc."""
 
    cpu_number = forms.IntegerField(min_value=0, label=_("CPU Number"))
    memory_size =  forms.IntegerField(min_value=0, label=_("RAM (GB)"))
    disk_size =  forms.IntegerField(min_value=0, label=_("DISK (GB)"))        
     
 
    def __init__(self, request,  context, *args, **kwargs):
        super(FillExtraAction, self).__init__(request, context, *args, **kwargs)          
        self.fields['cpu_number'].initial = self.initial.get("cpu_number", 0)
        self.fields['memory_size'].initial = self.initial.get("memory_size", 0)
        self.fields['disk_size'].initial = self.initial.get("disk_size", 0)
 
    class Meta(object):
        name = _("Extra")
        help_text = _("Add extra info of the node, such as cpu, memory etc.")
 
    def clean(self):
        cleaned_data = super(FillExtraAction, self).clean()        
        return cleaned_data
     
class FillExtraInfo(workflows.Step):
    action_class = FillExtraAction
    contributes = ("cpu_number", "memory_size", "disk_size")

 
 
 
class EditBasicAction(FillBasicAction):
    
    def __init__(self, request,  context, *args, **kwargs):
        super(EditBasicAction, self).__init__(request, context, *args, **kwargs)  
        self.fields['server_name'].initial = self.initial.get("server_name", '')
        self.fields['vendor_name'].initial = self.initial.get("vendor_name", '')
        self.fields['model'].initial = self.initial.get("model", '')
        
    class Meta(object):
        name = _("Basic Info")
        help_text = _("Basic info of the physical servers")
 
    def clean(self):
        cleaned_data = super(EditBasicAction, self).clean()        
        return cleaned_data
     
class EditBasicInfo(workflows.Step):
    action_class = EditBasicAction
    contributes = ("server_name", "vendor_name", "model")


class EditManagementAction(FillManagementAction):    
    server_uuid = forms.CharField(widget=forms.HiddenInput())
    def __init__(self, request,  context, *args, **kwargs):
        super(EditManagementAction, self).__init__(request, context, *args, **kwargs)  
        self.fields['server_uuid'].initial = self.initial.get("server_uuid", '')
        self.fields['ip_address'].initial = self.initial.get("ip_address", '')
        self.fields['user'].initial = self.initial.get("user", '')
        self.fields['password'].initial = self.initial.get("password", '')
        self.fields['port'].initial = self.initial.get("port", '')
 
    class Meta(object):
        name = _("Management Info")
        help_text = _("add ipmi authentication info of node")
 
    def clean(self):
        cleaned_data = super(EditManagementAction, self).clean()        
        return cleaned_data
     
class EditManagementInfo(workflows.Step):
    action_class = EditManagementAction
    contributes = ("ip_address", "user", "password", "port")
    
class EditExtraAction(FillExtraAction):
    
    def __init__(self, request,  context, *args, **kwargs):
        super(EditExtraAction, self).__init__(request, context, *args, **kwargs)          
        self.fields['cpu_number'].initial = self.initial.get("cpu_number", 0)
        self.fields['memory_size'].initial = self.initial.get("memory_size", 0)
        self.fields['disk_size'].initial = self.initial.get("disk_size", 0)
 
    class Meta(object):
        name = _("Extra")
        help_text = _("Add extra info of the node, such as cpu, memory etc.")
 
    def clean(self):
        cleaned_data = super(EditExtraAction, self).clean()        
        return cleaned_data
     
class EditExtraInfo(workflows.Step):
    action_class = EditExtraAction
    contributes = ("cpu_number", "memory_size", "disk_size")
 
 
 
class AddPhysicalServersWork(workflows.Workflow):
    slug = "add"
    name = _("Add Physical Servers")
    finalize_button_name = _("Add")
    success_message = _('Add physical servers successfully.')
    failure_message = _('Unable to add physical servers.')

    default_steps = (FillBasicInfo,
                     FillManagementInfo,
                     FillExtraInfo)
    wizard = True
  
    
    def get_success_url(self):
        return reverse("horizon:admin:physical_servers:index")
 
    def get_failure_url(self):
        return reverse("horizon:admin:physical_servers:index")
 
    def format_status_message(self, message):
        """if the message has format, we can make it in detail way"""
        return message 
 
    def handle(self, request, data):
        meta={}
        try:
            meta['ipmi_ip'] = data['ip_address']
            meta['ipmi_user'] = data['user']
            meta['ipmi_pass'] = data['password']
            meta['ipmi_port'] = data['port']
            meta['server_name'] = data['server_name']
            meta['vendor_name'] = data['vendor_name']
            meta['model'] = data['model']
            meta['cpu_number'] = data['cpu_number']
            meta['memory_size'] = data['memory_size']
            meta['disk_size'] = data['disk_size']
            
            api.ironic.add_ipmi_physical_server(request, **meta)
        except:
            msg=_('operation failed')
            messages.error(request, msg)
            exceptions.handle(request, msg)
            return False             
        return True






class EditPhysicalServersWork(workflows.Workflow):
    slug = "edit"
    name = _("Edit Physical Servers")
    finalize_button_name = _("Edit")
    success_message = _('Edit physical servers successfully.')
    failure_message = _('Unable to edit physical servers.')
    
    default_steps = (EditBasicInfo,
                     EditManagementInfo,
                     EditExtraInfo)
    wizard = False
    
    def get_success_url(self):
        return reverse("horizon:admin:physical_servers:index")
 
    def get_failure_url(self):
        return reverse("horizon:admin:physical_servers:index")
 
    def format_status_message(self, message):
        """if the message has format, we can make it in detail way"""
        return message 
        
    def handle(self, request, data):
        meta={}
        try:
            meta['ipmi_ip'] = data['ip_address']
            meta['ipmi_user'] = data['user']
            meta['ipmi_pass'] = data['password']
            meta['ipmi_port'] = data['port']
            meta['server_name'] = data['server_name']
            meta['vendor_name'] = data['vendor_name']
            meta['model'] = data['model']
            meta['cpu_number'] = data['cpu_number']
            meta['memory_size'] = data['memory_size']
            meta['disk_size'] = data['disk_size']
            
            api.ironic.edit_ipmi_physical_server(request, data['server_uuid'], **meta)
        except:
            msg=_('operation failed')
            messages.error(request, msg)
            exceptions.handle(request, msg)
            return False             
        return True
    
    
    