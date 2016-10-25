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


from collections import defaultdict
from django.utils.translation import ugettext_lazy as _
#from django.core.urlresolvers import reverse_lazy
#from django.template.defaultfilters import linebreaksbr
from horizon.utils import filters
from horizon import tables
from openstack_dashboard import api
from openstack_dashboard.dashboards.project.physical_servers\
        .tables import (PhysicalserversTable, \
                       DeployPhysicalServer, \
                       RebootPhysicalServer, ShutdownPhysicalServer,PoweronPhysicalServer,AssociateConsoleAuth)
from horizon import exceptions
from django.utils.translation import pgettext_lazy
from django.utils.translation import ungettext_lazy
from horizon import messages
from horizon.tables.base import Cell
from django.utils.safestring import mark_safe
import sys
import six
from django.utils.html import escape
from django import forms
from openstack_dashboard.dashboards.admin.physical_servers import driver_wrapper
import logging
LOG = logging.getLogger(__name__)
from django import template

class LenovoComputerSystemsCell(Cell):
    def get_data(self, datum, column, row):
        """Fetches the data to be displayed in this cell."""
        table = row.table
        if column.auto == "multi_select":
            data = ""
            if row.can_be_selected(datum):
                widget = forms.CheckboxInput(check_test=lambda value: False)
                # Convert value to string to avoid accidental type conversion
                data = widget.render('object_ids',
                                     unicode(table.get_object_id(datum)),
                                     {'class': 'table-row-multi-select'})
            table._data_cache[column][table.get_object_id(datum)] = data
        elif column.auto == "form_field":
            widget = column.form_field
            if issubclass(widget.__class__, forms.Field):
                widget = widget.widget

            widget_name = "%s__%s" % \
                (column.name,
                 unicode(table.get_object_id(datum)))

            # Create local copy of attributes, so it don't change column
            # class form_field_attributes
            form_field_attributes = {}
            form_field_attributes.update(column.form_field_attributes)
            # Adding id of the input so it pairs with label correctly
            form_field_attributes['id'] = widget_name

            if template.defaultfilters.urlize in column.filters:
                data = widget.render(widget_name,
                                     column.get_raw_data(datum),
                                     form_field_attributes)
            else:
                data = widget.render(widget_name,
                                     column.get_data(datum),
                                     form_field_attributes)
            table._data_cache[column][table.get_object_id(datum)] = data
        elif column.auto == "actions":
            data = table.render_row_actions(datum, pull_right=False)
            table._data_cache[column][table.get_object_id(datum)] = data
        else:
            data = column.get_data(datum)
            if column.cell_attributes_getter:
                cell_attributes = column.cell_attributes_getter(data) or {}
                self.attrs.update(cell_attributes)
        '''
        print("!!!!!!!!!!!!!!!!!!!!!!begin!!!!!!!!!!!!!!!!!!!!!!!!")
        print(data)
        data = _(unicode('<div class="glyphicon glyphicon-remove">') + unicode(data) + unicode('</div>'))
        print(data)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!end!!!!!!!!!!!!!!!!!!!!")
        return data
        '''
    @property
    def value(self):
        try:
            data = self.column.get_data(self.datum)
            if data is None:
                if callable(self.column.empty_value):
                    data = self.column.empty_value(self.datum)
                else:
                    data = self.column.empty_value
        except Exception:
            data = None
            exc_info = sys.exc_info()
            raise six.reraise(template.TemplateSyntaxError, exc_info[1],
                              exc_info[2])

        if self.url and not self.column.auto == "form_field":
            link_attrs = ' '.join(['%s="%s"' % (k, v) for (k, v) in
                                  self.column.link_attrs.items()])
            # Escape the data inside while allowing our HTML to render
            data = mark_safe('<a href="%s" %s>%s</a>' % (
                             (escape(self.url),
                              link_attrs,
                              escape(unicode(data)))))
        print("!!!!!!!!!!!!!!!!!!!!!!begin!!!!!!!!!!!!!!!!!!!!!!!!")
        print(data)
        if unicode(data) == 'OK':
            #data = mark_safe('&nbsp&nbsp<a href="#" class="tip-ok" title="OK!"><div class="glyphicon glyphicon-ok-circle" style="margin: 0 auto; color: #5CB85C; font-size:17px;"></div></a>')
            data = mark_safe('&nbsp&nbsp<div class="fa fa-square" style="margin: 0 auto; color: #5CB85C; font-size:17px;"></div>&nbsp OK')
            #data = mark_safe('<div class="glyphicon glyphicon-remove">%s</div>' % (
            #                    escape(unicode(data))))
        print(data)
        print("!!!!!!!!!!!!!!!!!!!!!!end!!!!!!!!!!!!!!!!!!!!!!!!")
        return data


class AdminRefreshPhysicalServer(tables.LinkAction):
    """click to pull data from xClarity to ironic DB and show on Horizon"""

    name = "refresh"
    verbose_name = _("Refresh Inventory")
    url = "horizon:admin:physical_servers:refresh"
    classes = ("ajax-modal",)
    ajax = True

class AdminRefreshInventory(tables.LinkAction):

    name = "refresh"
    verbose_name = _("Refresh Inventory")
    url = "horizon:admin:blades:refresh"
    classes = ("ajax-modal",)
    icon = "refresh"
    ajax = True

class AdminAssignPhysicalServers(tables.LinkAction):
    """assign servers to specified tenant, the options are in form """

    name = "Multi Assign"
    verbose_name = _("Assign Physical Servers")
    url = "horizon:admin:physical_servers:assigns"
    classes = ("ajax-modal", "btn-edit")

    def allowed(self, request, server=None):
        return True

class AdminAddPhiscalServer(tables.LinkAction):
    """add an standalone physical server(controlled by ipmi or other drivers, currently, ipmi driver) """

    name = "Add Servers"
    verbose_name = _("Add Physical Servers")
    url = "horizon:admin:physical_servers:add"
    classes = ("ajax-modal", "btn-edit")

    def allowed(self, request, server=None):
        return True


class AdminEditPhysicalServer(tables.LinkAction):
    """add an standalone physical server(controlled by ipmi or other drivers, currently, ipmi driver) """

    name = "Edit Servers"
    verbose_name = _("Edit Physical Servers")
    url = "horizon:admin:physical_servers:editserver"
    classes = ("ajax-modal", "btn-edit")

    def allowed(self, request, server=None):
        return driver_wrapper.check_if_edit_server_allowed(server)

class AdminPowerOnBlade(tables.BatchAction):
    name = "poweron_computer_system"
    action_present = _("Power On")
    action_past = _("power on")
    data_type_singular = _(" ")
    data_type_plural = _(" ")
    classes = ("btn-reboot")

    def allowed(self, request, server=None):
        if server and server.power_state == 'On':
            return False
        else:

            return True
    def action(self, request, obj_id):
        pass

class AdminRebootBlade(tables.BatchAction):
    name = "reboot_blade"
    verbose_name = _("Reboot")
    classes = ("btn-reboot",)

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Reboot",
            u"Reboot",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Successfully Reboot this Blade",
            u"Successfully Reboot this Blade",
            count
        )

    def allowed(self, request, server=None):
        if server and server.power_state != 'On':
            return False
        else:
            return True

    def action(self, request, obj_id):
        pass


class AdminPowerOffBlade(tables.BatchAction):
    name = "poweroff_computer_system"
    verbose_name = _("Power Off")
    classes = ("btn-danger",)

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"PowerOff",
            u"PowerOff",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Successfully PowerOff this Computer System",
            u"Successfully PowerOff Computer Systems",
            count
        )

    def allowed(self, request, server=None):
        return True
    def action(self, request, obj_id):
        pass

class AdminFreePysicalServers(tables.BatchAction):
    """Free Physical Servers, we can only free those servers reserved"""

    name = "batch_free"
    icon="plus"
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Free Physical Server",
            u"Free Physical Servers",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Freed Physical Server",
            u"Freed Physical Servers",
            count
        )


    def allowed(self, request, server=None):
        #only reserved servers can be freed
        return driver_wrapper.check_if_free_server_allowed(server)

    def action(self, request, obj_id):
        api.ironic.change_server_category(request, obj_id, "free_node_by_uuid")

class AdminReservePysicalServers(tables.BatchAction):
    """Reserve Physical Servers"""

    name = "batch_reserve"
    icon="pencil"
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Reserve Physical Server",
            u"Reserve Physical Servers",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Reserved Physical Server",
            u"Reserved Physical Servers",
            count
        )


    def allowed(self, request, server=None):
        #only reserved servers can be freed
        return driver_wrapper.check_if_reserve_server_allowed(server)

    def action(self, request, obj_id):
        api.ironic.change_server_category(request, obj_id, "reserve_node_by_uuid")

class AdminRemovePysicalServers(tables.BatchAction):
    """Reserve Physical Servers"""

    name = "batch_remove"
    icon="pencil"
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Remove Physical Server",
            u"Remove Physical Servers",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Removed Physical Server",
            u"Removed Physical Servers",
            count
        )


    def allowed(self, request, server=None):
        #only reserved servers can be freed
        return driver_wrapper.check_if_remove_server_allowed(server)

    def action(self, request, obj_id):
        api.ironic.remove_physical_server(request, obj_id)

class AdminForceRemovePysicalServers(tables.BatchAction):
    """Reserve Physical Servers"""

    name = "batch_force_remove"
    icon="pencil"
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Force Remove Physical Server",
            u"Force Remove Physical Servers",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Force Removed Physical Server",
            u"Force Removed Physical Servers",
            count
        )


    def allowed(self, request, server=None):
        #only reserved servers can be freed
        return True

    def action(self, request, obj_id):
        api.ironic.remove_physical_server(request, obj_id)

class AdminDeployPhysicalServer(DeployPhysicalServer):
    """Admin Deploy physical server OS, current both Admin and Project users can do the Deploy"""

    url = "horizon:admin:physical_servers:deploy"

    def allowed(self, request, server):
        return driver_wrapper.check_if_deploy_action_allowed(server)

class AdminAssociateHypervisor(tables.LinkAction):
    """associate imm user/pass with the server"""

    name = "hypervizor"
    verbose_name = _("Associate Nova Host")
    url = "horizon:admin:physical_servers:hypervizor"
    classes = ("ajax-modal", "btn-edit")

    def allowed(self, request, server):
        if server.xclarity_ip != '' :
            return True
        else:
            return False

class AdminDeassociateHypervisor(tables.BatchAction):
    """deassociate with nova hypervisor"""

    name = "deassociate_hypervisor"

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Physical Server unlinked with hypervisor",
            u"Physical Servers unlinked with hypervisor",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Physical Server unlinked with hypervisor",
            u"Physical Servers unlinked with hypervisor",
            count
        )

    def action(self, request, obj_id):
        #reserve the selected server
        api.ironic.associate_hypervisor(request, obj_id,'','')

    def allowed(self, request, server):
        if server.hypervisor != '' :
            return True
        else:
            return False

class AdminAssociateConsoleAuth(AssociateConsoleAuth):
    """associate imm user/passwd"""
    url = "horizon:admin:physical_servers:associate_auth"

    def allowed(self, request, server):
        return driver_wrapper.check_if_console_auth_allowed(server)

class AdminRebootPhysicalServer(RebootPhysicalServer):
    """Currently, the Admin can do the reboot the same as project users"""
    pass

class AdminShutdownPhysicalServer(ShutdownPhysicalServer):
    """Currently, the Admin can do the shutdown the same as project users"""
    pass

class AdminPoweronPhysicalServer(PoweronPhysicalServer):
    """Currently, the Admin can do the power on the same as project users"""
    pass

class AdminReservePhysicalServer(tables.BatchAction):
    """
    Admin can reserve physical server from public to reserved status,
    once reserved, no projects(other tenant) can touch this server
    """

    name = "reserved"
    action_present = _("Reserve")
    action_past = _("Scheduled reserved of")
    data_type_singular = _("Physical Server")
    data_type_plural = _("Physical Servers")
    classes = ("btn-danger", "btn-reboot")

    def allowed(self, request, server=None):
        return driver_wrapper.check_if_reserve_server_allowed(server)

    def action(self, request, obj_id):
        #reserve the selected server
        api.ironic.change_server_category(request, obj_id, "reserve_node_by_uuid")


class AdminRemovePhysicalServer(tables.BatchAction):
    """
    remove the node from list, once the node is disconnected, we provide a way to remove this node
    """

    name = "remove_server"
    action_present = _("Remove")
    action_past = _("Scheduled reserved of")
    data_type_singular = _("Physical Server")
    data_type_plural = _("Physical Servers")
    classes = ("btn-danger", "btn-reboot")

    def allowed(self, request, server=None):
        return driver_wrapper.check_if_remove_server_allowed(server)

    def action(self, request, obj_id):
        #reserve the selected server
        api.ironic.remove_physical_server(request, obj_id)

class AdminForceRemovePhysicalServer(tables.BatchAction):
    """
    remove the node from list, once the node is disconnected, we provide a way to remove this node
    when unmanage xclarity, we need to remove these
    """

    name = "force_remove_server"
    action_present = _("Force Remove")
    action_past = _("Scheduled reserved of")
    data_type_singular = _("Physical Server")
    data_type_plural = _("Physical Servers")
    classes = ("btn-danger", "btn-reboot")

    def allowed(self, request, server=None):
        return True

    def action(self, request, obj_id):
        #reserve the selected server
        api.ironic.remove_physical_server(request, obj_id)


class AdminFreePhysicalServer(tables.BatchAction):
    """row action, to free a specified server"""

    name = "free"
    action_present = _("Free")
    action_past = _("Scheduled free of")
    data_type_singular = _("Physical Server")
    data_type_plural = _("Physical Servers")
    classes = ("btn-danger", "btn-reboot")

    def allowed(self, request, server=None):
        return driver_wrapper.check_if_free_server_allowed(server)

    def action(self, request, obj_id):
        #we can combine the free_servers and free_server
        api.ironic.change_server_category(request, obj_id, "free_node_by_uuid")

class FilterAction(tables.FilterAction):
    def filter(self, table, servers, filter_string):
        """Really naive case-insensitive search."""
        q = filter_string.lower()

        def comp(server):
            #currently, we see what happened if we use the name as the filter key word
            return q in server.name.lower()

        return filter(comp, servers)

class AdminBladesFilterAction(tables.FilterAction):
    name = "filter_admin_blades"
    filter_type = "query"

class AdminOwnerFilter(tables.FixedFilterAction):
    """build category for server table"""

    def get_fixed_buttons(self):
        def make_dict(text, user, icon):
            return dict(text=text, value=user, icon=icon)
        buttons = [make_dict(_('Public Free'), 'public_free', 'fa-star')]
        buttons.append(make_dict(_('Public Assigned'), 'public_assigned', 'fa-fire'))
        buttons.append(make_dict(_('Reserved'), 'reserved', 'fa-home'))

        return buttons

    def categorize(self, table, servers):
        #the rules to categorize servers
        types = defaultdict(list)
        for server in servers:
            categories = get_server_categories(server)
            for category in categories:
                types[category].append(server)
        return types

def get_server_categories(server):
    """mark servers as different category"""
    categories = []
    if server.assigned=='0':
        categories.append('public_free')
    elif server.assigned=='-1':
        categories.append('reserved')
    else:
        categories.append('public_assigned')
    return categories


class UpdateRow(tables.Row):
    """The way to load table rows and cells"""
    ajax = True

    def get_data(self, request, uuid):
        server = api.ironic.physical_server_get(request, uuid)
        return server

    def load_cells(self, server=None):
        super(UpdateRow, self).load_cells(server)
        #Tag the row with the server category for client-side filtering.
        server = self.datum
        #my_user_id = self.table.request.user.id
        server_categories = get_server_categories(server)
        #we can do more here, currently, this is useless
        for category in server_categories:
            self.classes.append('category-' + category)


class AdminPhysicalserversTable(PhysicalserversTable):
    """Admin Physcial server view"""

    TASK_STATUS_CHOICES = (
        (None, None),
        ('', False),
        ("none", None),
        ("Ready", True),
        ("Not Ready", False),
        ("available", True),
        ("active", True),
        ("deploy failed", False),
        ("deploy complete", True),
        ("deleted", False),
    )

    TASK_DISPLAY_CHOICES = (
    ("Ready", pgettext_lazy("Task status of a deploy process",u"Ready")),
    ("Not Ready", pgettext_lazy("Task status of a deploy process",u"Not Ready")),
    ("Deploying", pgettext_lazy("Task status of a deploy process",u"Deploying")),
    ("available", pgettext_lazy("Task status of a deploy process",u"Available")),
    ("active", pgettext_lazy("Task status of a deploy process",u"Active")),
    ("deploy failed", pgettext_lazy("Task status of a deploy process",u"Deploy failed")),
    ("deploy complete", pgettext_lazy("Task status of a deploy process",u"Deploy complete")),
    ("deleting", pgettext_lazy("Task status of a deploy process",u"Deleting")),
    ("deleted", pgettext_lazy("Task status of a deploy process",u"Deleted")),
    )

    #in the future, the admin side detail/ready check may different with the project user side
    #currently, to make it simple, we assume they are the same
    project = tables.Column("project", verbose_name=_("Project"))
    name = tables.Column("name",
                         link=("horizon:admin:physical_servers:"
                               "detail"),
                         verbose_name=_("Server Name"),
                         classes=('glyphicon-class', 'glyphicon-envelope',),
                        )
    hypervisor = tables.Column("hypervisor",
                         link=("horizon:admin:hypervisors:"),
                         verbose_name=_("Associate hypervisor"))
    provision_state  = tables.Column("provision_state",
                          verbose_name= _("Provision State"),
                          link=("horizon:admin:physical_servers:"
                               "readycheck"),
                          status=True,
                          status_choices=TASK_STATUS_CHOICES,
                          display_choices=TASK_DISPLAY_CHOICES,
                          )

    class Meta:
        name = "physicalservers"
        verbose_name = _("Physical Server in xClarity")
        status_columns = ["power_state", "provision_state"]
        row_class = UpdateRow
        columns = ["name","product_name", "management_ip","provision_state","power_state", "project", "hyervizor", ]

        table_actions_menu = (AdminAssignPhysicalServers, AdminFreePysicalServers, AdminReservePysicalServers, AdminRemovePysicalServers,
                              AdminForceRemovePysicalServers)
        #admin side physical servers operations view
        table_actions = (AdminOwnerFilter, AdminAddPhiscalServer, AdminRefreshPhysicalServer)

        #more row actions to add here, such as refresh the selected server, associate port(pxe deploy)
        row_actions = (AdminDeployPhysicalServer, AdminRebootPhysicalServer, AdminShutdownPhysicalServer,
                       AdminPoweronPhysicalServer, AdminFreePhysicalServer, AdminReservePhysicalServer,
                       AdminRemovePhysicalServer, AdminForceRemovePhysicalServer, AdminEditPhysicalServer,
                       AdminAssociateConsoleAuth, AdminAssociateHypervisor, AdminDeassociateHypervisor)
        cell_class = LenovoComputerSystemsCell


"""
=============================================================================================
Heterogeneous servers table, what is the design?
we make the user can add CIM driver server? or ?
"""

"""
=============================================================================================
"""


class UpdateApprovalRow(tables.Row):
    ajax = True

    def get_data(self, request, subscribe_id):
        """get the approval row from DB"""

        server = api.ironic.get_subscribe(request, subscribe_id)
        return server


class RefreshApprovalRefresh(tables.LinkAction):
    """refresh to retrieve the approval list from DB"""

    name = "refresh_approve"
    verbose_name = _("Refresh List")
    url = "horizon:admin:physical_servers:refresh_approval"
    classes = ("ajax-modal",)
    ajax = True

class BatchApprove(tables.BatchAction):
    """batch approve the requests"""

    name = "batch_approve"
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Approve Subscription",
            u"Approve Subscriptions",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Approved Subscription",
            u"Approved Subscriptions",
            count
        )


    def allowed(self, request, server=None):
        return True

    def action(self, request, obj_id):
        try:
            subscription = api.ironic.get_subscribe(request, obj_id)
            filter_items={}
            filter_items['assign_number'] = subscription.number
            filter_items['target_tenant'] = subscription.tenant_id
            filter_items['target_tenant_name'] = subscription.tenant_name
            filter_items['flavor_id'] = subscription.flavor_id
            filter_items['flavor_name'] = subscription.flavor_name
            filter_items['rules'] = subscription.rule
            filter_items['direction'] = 'project'
            res = api.ironic.assign_servers(request, **filter_items)
            if res == 'Assigned successfully':
                #only success, we destroy it
                api.ironic.reject_subscribe_request(request, obj_id)
            else:
                msg=_('operation failed, please check if enough servers in resource pool met the requirement')
                messages.error(request, msg)
                return
        except Exception:
            exceptions.handle(request,
                              _('check the resource pool.'))

class BatchReject(tables.BatchAction):
    """batch reject the requests"""

    name = "batch_reject"
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Reject Subscription",
            u"Reject Subscriptions",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Rejected Subscription",
            u"Rejected Subscriptions",
            count
        )


    def allowed(self, request, server=None):
        return True

    def action(self, request, obj_id):
        api.ironic.reject_subscribe_request(request, obj_id)

class AdminApproval(tables.BatchAction):
    """Approve the Request from Users"""

    name = "approval"
    action_present = _("Approve")
    action_past = _("Scheduled approval of")
    data_type_singular = _("Request")
    data_type_plural = _("Requests")
    classes = ("btn-danger", "btn-reboot")

    def allowed(self, request, server=None):
        return True

    def action(self, request, obj_id):
        try:
            subscription = api.ironic.get_subscribe(request, obj_id)
            filter_items={}
            filter_items['assign_number'] = subscription.number
            filter_items['target_tenant'] = subscription.tenant_id
            filter_items['target_tenant_name'] = subscription.tenant_name
            filter_items['flavor_id'] = subscription.flavor_id
            filter_items['flavor_name'] = subscription.flavor_name
            filter_items['rules'] = subscription.rule
            filter_items['direction'] = 'project'
            res = api.ironic.assign_servers(request, **filter_items)
            if res == 'Assigned successfully':
                #only success, we destroy it
                api.ironic.reject_subscribe_request(request, obj_id)
            else:
                msg=_('operation failed, please check if enough servers in resource pool met the requirement')
                messages.error(request, msg)
                #raise Exception(msg)
        except Exception:
            exceptions.handle(request,
                              _('check the resource pool.'))

class AdminReject(tables.BatchAction):
    """Reject the request from Users"""

    name = "reject"
    action_present = _("Reject")
    action_past = _("Scheduled reject of")
    data_type_singular = _("Request")
    data_type_plural = _("Requests")
    classes = ("btn-danger", "btn-reboot")

    def allowed(self, request, server=None):
        return True

    def action(self, request, obj_id):
        api.ironic.reject_subscribe_request(request, obj_id)

class AdminApprovalListTable(tables.DataTable):
    """Admin view, approval list"""

    tenant_name = tables.Column("tenant_name",
                         verbose_name=_("Tenant Name"))
    flavor_name = tables.Column("flavor_name",
                         verbose_name=_("Flavor Name"))
    flavor_id = tables.Column("flavor_id",
                         verbose_name=_("Flavor ID"))
    tenant_id = tables.Column("tenant_id",
                         verbose_name=_("Tenant ID"))
    rule = tables.Column("rule",
                         verbose_name=_("Rule"))
    number = tables.Column("number",
                         verbose_name=_("Number"))

    def get_object_id(self, datum):

        return datum.id

    class Meta:
        name = "approvallist"
        verbose_name = _("ApprovalList")
        columns = ["tenant_name", "flavor_name","flavor_id","rule", "number"]
        row_class = UpdateApprovalRow
        table_actions = (BatchApprove, BatchReject, RefreshApprovalRefresh,)
        row_actions = (AdminApproval, AdminReject)

"""
=============================================================================================
"""
class ManageXClarity(tables.LinkAction):
    """
    assign servers to specified tenant
    """
    name = "Manage XClarity"
    verbose_name = _("Manage XClarity")
    url = "horizon:admin:physical_servers:manage"
    classes = ("ajax-modal", "btn-edit")

    def allowed(self, request, xhmc=None):
        return True

class EditXClarity(tables.LinkAction):
    """
    assign servers to specified tenant
    """
    name = "Edit XClarity"
    verbose_name = _("Edit XClarity")
    url = "horizon:admin:physical_servers:edit_xclarity"
    classes = ("ajax-modal", "btn-edit")

    def allowed(self, request, xhmc=None):
        return True

class ConfigXClarity(tables.LinkAction):
    """
    config the xclarity to use dhcp/static ip
    """
    name = "Configure XClarity"
    verbose_name = _("Configure XClarity")
    url = "horizon:admin:physical_servers:config"
    classes = ("ajax-modal", "btn-edit")

    def allowed(self, request, xhmc=None):
        return True

class UnManageXClarity(tables.BatchAction):

    name = "batch_unmanage"
    icon="pencil"
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Unmanage XClarity",
            u"Unmanage XClarities",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Unmanaged XClarity",
            u"Unmanaged XClarities",
            count
        )


    def allowed(self, request, xhmc=None):
        return True

    def action(self, request, obj_id):
        api.ironic.unmanage_xclarity(request, obj_id)

class UnManage(tables.BatchAction):
    """project user apply server in assigned servers"""

    name = "unmanage"
    action_present = _("Remove")
    action_past = _("Scheduled application of")
    data_type_singular = _("XClarity")
    data_type_plural = _("XClarities")
    classes = ("btn-danger", "btn-reboot")

    def allowed(self, request, datum):
        return True


    def action(self, request, obj_id):
        api.ironic.unmanage_xclarity(request, obj_id)

class UpdateXClarityRow(tables.Row):
    ajax = True

    def get_data(self, request, xclarity_id):
        xclarity_inst = api.ironic.get_xclarity(request, xclarity_id)
        return xclarity_inst

def get_link(xhmc):
    """Get the xClarity link"""
    if hasattr(xhmc, "link"):
        template_name = 'admin/physical_servers/xhmc_link.html'
        link=xhmc.link
        context = {
            "id":xhmc.id,
            "link": link,
            "ipaddress":xhmc.ipaddress
        }
        return template.loader.render_to_string(template_name, context)
    return _("Not available")

class AdminXClarityManagementTable(tables.DataTable):
    """Admin side xClarity management view"""

    ipaddress = tables.Column("ipaddress",
                         verbose_name=_("Ip Address"))
    username = tables.Column("username",
                         verbose_name=_("User"))
    password = tables.Column("password",
                         verbose_name=_("Password"))
    link = tables.Column(get_link,
                         verbose_name=_("Link"))
    state = tables.Column("state",
                         verbose_name=_("Status"))


    class Meta:
        name = "xclaritymanagement"
        verbose_name = _("xClarity Management")
        columns = ["ipaddress", "username","state", "link"]
        row_class = UpdateXClarityRow
        table_actions = (ManageXClarity,UnManageXClarity, ConfigXClarity,)
        row_actions = (UnManage, EditXClarity,)

class AdminBladeTable(tables.DataTable):
    TASK_STATUS_CHOICES = (
        (None, True),
        ("none", True)
    )
    STATUS_CHOICES = (
        ("active", True),
        ("shutoff", True),
        ("suspended", True),
        ("paused", True),
        ("error", False),
        ("rescue", True),
        ("shelved", True),
        ("shelved_offloaded", True),
    )
    #tenant = tables.Column("tenant_name", verbose_name=_("Project"))
    #host = tables.Column("OS-EXT-SRV-ATTR:host",
    #                     verbose_name=_("Host"),
    #                     classes=('nowrap-col',))
    name = tables.Column("name",
                         link=("horizon:admin:blades:"
                               "detail"),
                         verbose_name=_("Name"))
    status_2 = tables.Column("status_2",
                         verbose_name=_("Status"))
    model = tables.Column("model",
                         verbose_name=_("Model"))
    hostname = tables.Column("hostname",
                         verbose_name=_("Hostname"))
    '''
    rack_2 = tables.Column("rack_2",
                         verbose_name=_("Rack"))
    u_location = tables.Column("u_location",
                         verbose_name=_("Location"))
    '''
    location_summary = tables.Column("location_summary",
                         verbose_name=_("Location"))
    description = tables.Column("description",
                         verbose_name=_("Description"))

    class Meta(object):
        name = "blades"
        verbose_name = _("Computer Systems")
        table_actions = (AdminBladesFilterAction,
                         AdminRefreshInventory,
                         AdminPowerOnBlade,
                         AdminRebootBlade,
                         AdminPowerOffBlade,
                         )
        row_actions = (AdminPowerOnBlade,
                       AdminRebootBlade,
                       AdminPowerOffBlade,
                      )
        cell_class = LenovoComputerSystemsCell
        '''
        status_columns = ["status", "task"]
        table_actions = (project_tables.TerminateInstance,
                         AdminPcieswitchesFilterAction)
        row_class = AdminUpdateRow
        row_actions = (project_tables.ConfirmResize,
                       project_tables.RevertResize,
                       AdminEditInstance,
                       project_tables.ConsoleLink,
                       project_tables.LogLink,
                       project_tables.CreateSnapshot,
                       project_tables.TogglePause,
                       project_tables.ToggleSuspend,
                       MigrateInstance,
                       LiveMigrateInstance,
                       project_tables.SoftRebootInstance,
                       project_tables.RebootInstance,
                       project_tables.TerminateInstance)
        '''

class EventlogTable(tables.DataTable):
    request_id = tables.Column('request_id',
                               verbose_name=_('Request ID'))
    action = tables.Column('action', verbose_name=_('Action'))
    start_time = tables.Column('start_time', verbose_name=_('Start Time'),
                               filters=[filters.parse_isotime])
    user_id = tables.Column('user_id', verbose_name=_('User ID'))
    message = tables.Column('message', verbose_name=_('Message'))

    class Meta(object):
        name = 'audit'
        verbose_name = _('Instance Action List')

    def get_object_id(self, datum):
        return datum.request_id



