# Copyright 2015 Lenovo.
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
#    under the License. fields

"""
Forms of Physical server Panel
"""
from horizon import forms
from openstack_dashboard import api
from horizon import messages
from horizon import exceptions
from django.utils.translation import ugettext_lazy as _
from horizon.utils import validators


class RefreshServerForm(forms.SelfHandlingForm):

    def __init__(self, request, *args, **kwargs):
        super(RefreshServerForm, self).__init__(request, *args, **kwargs)

    def handle(self, request, data):
        try:
            request = self.request
            self._more = True
            try:
                if 'SELECTED_POD_MANAGER_ID' not in self.request.session:
                    pod_id = 1
                else:
                    pod_id = self.request.session['SELECTED_POD_MANAGER_ID']
                api.rsa.composed_servers_list(request, pod_id, refresh=True)
            except:
                exceptions.handle(request,
                                _('Unable to retrieve pod managers list.'))
            #api.ironic.physical_server_list(request, refresh=True)
            message = _('Inventory successfully Refreshed.')
            messages.success(request, message)
            return True
        except Exception:
            exceptions.handle(request,
                              _('Unable to refresh the inventory.'))

class RefreshApprovalServerForm(forms.SelfHandlingForm):
    """pull the subscriptions from DB"""

    def __init__(self, request, *args, **kwargs):
        super(RefreshApprovalServerForm, self).__init__(request, *args, **kwargs)

    def handle(self, request, data):
        try:
            api.ironic.get_subscribe(request)
            message = _('Approval list successfully Refreshed.')
            messages.success(request, message)
            return True
        except Exception:
            exceptions.handle(request,
                              _('Unable to refresh the approval list.'))


class ManageForm(forms.SelfHandlingForm):
    """Manage xClariy, Multi xClarities supported"""

    ip_address = forms.CharField(max_length="255",
                                label=_("IP Address"),
                                help_text=_("The IP address of xClarity Administrator."),
                                required=True)
    user = forms.CharField(max_length="255",
                                label=_("User Name"),
                                help_text=_("User name of xClarity Administrator."),
                                required=True)
    #password = forms.CharField(max_length="255",
    #                    label=_("Password"),
    #                    help_text=_("Password of xClarity Administrator."),
    #                    required=True
    #                    )
    password = forms.RegexField(
        label=_("Password"),
        widget=forms.PasswordInput(render_value=True),
        help_text=_("Password of xClarity Administrator."),
        regex=validators.password_validator(),
        error_messages={'invalid': validators.password_validator_msg()})

    def __init__(self, request, *args, **kwargs):
        super(ManageForm, self).__init__(request, *args, **kwargs)


    def handle(self, request, data):
        try:
            ip=data['ip_address']
            user=data['user']
            passwd=data['password']
            api.ironic.manage_xclarity(request, ip, user, passwd)
            message = _('Manage xClarity successfully.')
            messages.success(request, message)
            return True
        except Exception:
            exceptions.handle(request,
                              _('Unable to manage xClarity.'))

class EditForm(forms.SelfHandlingForm):
    """Manage xClariy, Multi xClarities supported"""
    xclarity_id = forms.CharField(widget=forms.HiddenInput())
    ip_address = forms.CharField(max_length="255",
                                label=_("IP Address"),
                                help_text=_("The IP address of xClarity Administrator."),
                                required=True)
    user = forms.CharField(max_length="255",
                                label=_("User Name"),
                                help_text=_("User name of xClarity Administrator."),
                                required=True)
    password = forms.RegexField(
        label=_("Password"),
        widget=forms.PasswordInput(render_value=True),
        help_text=_("Password of xClarity Administrator."),
        regex=validators.password_validator(),
        error_messages={'invalid': validators.password_validator_msg()})

    def __init__(self, request, *args, **kwargs):
        super(EditForm, self).__init__(request, *args, **kwargs)
        self.fields['ip_address'].initial = kwargs['initial']['xclarity_ip']
        self.fields['user'].initial = kwargs['initial']['xclarity_user']
        self.fields['password'].initial = kwargs['initial']['xclarity_passwd']

    def handle(self, request, data):
        try:
            xclarity_id=data['xclarity_id']
            ip=data['ip_address']
            user=data['user']
            passwd=data['password']
            api.ironic.edit_xclarity(request, xclarity_id, ip, user, passwd)
            message = _('Edit xClarity successfully.')
            messages.success(request, message)
            return True
        except Exception:
            exceptions.handle(request,
                              _('Unable to edit xClarity.'))

class HypervisorForm(forms.SelfHandlingForm):
    """Associate nova host for physical server"""

    failure_url = 'horizon:admin:physical_servers:index'

    uuid = forms.CharField(widget=forms.HiddenInput())

    available_hypervisor = forms.ChoiceField(
        label=_("Available host in nova"),
        help_text=_("The host that running nova compute service.It should be identical as this physical server"),
        choices=[],
        required=True,
        widget=forms.Select(attrs={'class':'switchable'})
    )

    auto_evacuate = forms.BooleanField(
        label=_("Automatic VM evacuation"),
        help_text=_("The host will try to evacuate VMs to specified hosts when predictable failure alert detected"),
        required=False
    )

    alert_key = forms.CharField(
        max_length="100",
        label=_("Only match alerts with following keywords"),
        help_text=_("The auto VM evacuation will not happen unless the alert containing following keywords"),
        required=False
    )

    dest_hypervisor = forms.ChoiceField(
        label=_("Target host for VM migration"),
        help_text=_("The host that VM will be migrated to when this server is about to fail"),
        choices=[],
        required=True,
        widget=forms.Select(attrs={'class':'switchable'})
    )

    def __init__(self, request, *args, **kwargs):
        super(HypervisorForm, self).__init__(request, *args, **kwargs)
        hypervisors = []
        hypervisor_list = api.nova.hypervisor_list(request)
        hypervisor_choice = []
        for hypervisor in hypervisor_list:
            hypervisor_choice.append((hypervisor.id, hypervisor.hypervisor_hostname + '(' + hypervisor.hypervisor_type + ')'))
        self.fields['available_hypervisor'].choices = hypervisor_choice
        target_choice = hypervisor_choice
        target_choice.insert(0, (0, "Any available host"))
        self.fields['dest_hypervisor'].choices = target_choice

    def handle(self, request, data):
        try:
            api.ironic.associate_hypervisor(request, data['uuid'], data['available_hypervisor'],data['auto_evacuate'],data['alert_key'],data['dest_hypervisor'])
            messages.success(request, _('succeed to associate the nova compute host.'))
            return True
        except Exception:
            exceptions.handle(request, _("Failed to associate the nova compute host"))


class ConfigForm(forms.SelfHandlingForm):
    """configure xClariy, for all xclarities"""

    ip_assignment = forms.ChoiceField(
        label=_("IP Assignment Method"),
        help_text=_("The IP assignment way while deploying OS."),
        choices=[('', _('Select IP Assignment Method')),
                 ('staticv4',_('Static Way')),
                 ('dhcpv4',_('DHCP Way')),
                 ],
        required=True,
        widget=forms.Select(attrs={'class':'switchable'})
    )

    def __init__(self, request, *args, **kwargs):
        super(ConfigForm, self).__init__(request, *args, **kwargs)
        ip_way = api.ironic.get_global_settings(request)
        if ip_way:
            self.fields['ip_assignment'].initial = ip_way
        else:
            raise Exception('unable to get the ip assignment, please check the Xclarities')

    def handle(self, request, data):
        try:
            ip_way=data['ip_assignment']
            api.ironic.configure_xclarity(request, ip_way)
            message = _('Configure xClarity successfully.')
            messages.success(request, message)
            return True
        except Exception:
            exceptions.handle(request,
                              _('Unable to Configure xClarity.'))

