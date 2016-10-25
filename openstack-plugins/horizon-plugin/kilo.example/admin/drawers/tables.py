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
from django.template.defaultfilters import title  # noqa
from django.utils.translation import ugettext_lazy as _
#from django.core.urlresolvers import reverse_lazy
#from django.template.defaultfilters import linebreaksbr
from horizon.utils import filters
from horizon import tables
from openstack_dashboard import api
from openstack_dashboard import policy
from openstack_dashboard.dashboards.project.instances \
    import tables as project_tables
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

class AdminEditInstance(project_tables.EditInstance):
    url = "horizon:admin:instances:update"

class MigrateInstance(policy.PolicyTargetMixin, tables.BatchAction):
    name = "migrate"
    classes = ("btn-migrate", "btn-danger")
    policy_rules = (("compute", "compute_extension:admin_actions:migrate"),)
    help_text = _("Migrating instances may cause some unrecoverable results.")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Migrate Instance",
            u"Migrate Instances",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Scheduled migration (pending confirmation) of Instance",
            u"Scheduled migration (pending confirmation) of Instances",
            count
        )

    def allowed(self, request, instance):
        return ((instance.status in project_tables.ACTIVE_STATES
                 or instance.status == 'SHUTOFF')
                and not project_tables.is_deleting(instance))

    def action(self, request, obj_id):
        api.nova.server_migrate(request, obj_id)


class LiveMigrateInstance(policy.PolicyTargetMixin,
                          tables.LinkAction):
    name = "live_migrate"
    verbose_name = _("Live Migrate Instance")
    url = "horizon:admin:instances:live_migrate"
    classes = ("ajax-modal", "btn-migrate", "btn-danger")
    policy_rules = (
        ("compute", "compute_extension:admin_actions:migrateLive"),)

    def allowed(self, request, instance):
        return ((instance.status in project_tables.ACTIVE_STATES)
                and not project_tables.is_deleting(instance))

class AdminUpdateRow(project_tables.UpdateRow):
    def get_data(self, request, instance_id):
        instance = super(AdminUpdateRow, self).get_data(request, instance_id)
        tenant = api.keystone.tenant_get(request,
                                         instance.tenant_id,
                                         admin=True)
        instance.tenant_name = getattr(tenant, "name", None)
        return instance

class AdminPcieswitchesFilterAction(tables.FilterAction):
    name = "filter_admin_pcie_switches"
    filter_type = "query"
    '''
    filter_choices = (('project', _("Project ="), True),
                      ('host', _("Host ="), True),
                      ('name', _("Name"), True),
                      ('ip', _("IPv4 Address ="), True),
                      ('ip6', _("IPv6 Address ="), True),
                      ('status', _("Status ="), True),
                      ('image', _("Image ID ="), True),
                      ('flavor', _("Flavor ID ="), True))
    '''

class LenovoDrawersCell(Cell):
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
        '''
        return data
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
            #data = mark_safe('&nbsp&nbsp<a href="#" class="tip-ok" title="OK!"><div class="fa fa-square" style="margin: 0 auto; color: #5CB85C; font-size:17px;"></div>&nbsp OK</a>')
            data = mark_safe('&nbsp&nbsp<div class="fa fa-square" style="margin: 0 auto; color: #5CB85C; font-size:17px;"></div>&nbsp OK')
        print(data)
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
    url = "horizon:admin:drawers:refresh"
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
    '''
    if server.assigned=='0':
        categories.append('public_free')
    elif server.assigned=='-1':
        categories.append('reserved')
    else:
        categories.append('public_assigned')
    '''
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

class AdminDrawersTable(tables.DataTable):
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
                         link=("horizon:admin:drawers:"
                               "detail"),
                         verbose_name=_("Name"))
    # chassis_type = tables.Column("type",
                         # verbose_name=_("Type"))
    status_2 = tables.Column(
        "status_2",
        #filters=(title, filters.replace_underscores),
        verbose_name=_("Status"),
        status=True,
        status_choices=STATUS_CHOICES,
        display_choices=project_tables.STATUS_DISPLAY_CHOICES)
    model = tables.Column("model",
                         verbose_name=_("Model"))
    serial_number = tables.Column("serial_number",
                         verbose_name=_("Serial Number"))
    '''
    rack = tables.Column("rack",
                         verbose_name=_("Rack"))
    location = tables.Column("location",
                         verbose_name=_("Location"))
    '''
    location_summary = tables.Column("location_summary",
                         verbose_name=_("Location"))
    description = tables.Column("description",
                         verbose_name=_("Description"))
    '''
    image_name = tables.Column("image_name",
                               verbose_name=_("Image Name"))
    size = tables.Column(project_tables.get_size,
                         verbose_name=_("Size"),
                         attrs={'data-type': 'size'})
    task = tables.Column("OS-EXT-STS:task_state",
                         verbose_name=_("Task"),
                         empty_value=project_tables.TASK_DISPLAY_NONE,
                         status=True,
                         status_choices=TASK_STATUS_CHOICES,
                         display_choices=project_tables.TASK_DISPLAY_CHOICES)
    state = tables.Column(project_tables.get_power_state,
                          filters=(title, filters.replace_underscores),
                          verbose_name=_("Power State"),
                          display_choices=project_tables.POWER_DISPLAY_CHOICES)
    created = tables.Column("created",
                            verbose_name=_("Time since created"),
                            filters=(filters.parse_isotime,
                                     filters.timesince_sortable),
                            attrs={'data-type': 'timesince'})
    '''

    class Meta(object):
        name = "drawers"
        verbose_name = _("Drawers")
        table_actions = (AdminPcieswitchesFilterAction, AdminRefreshInventory, )
        cell_class = LenovoDrawersCell
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
