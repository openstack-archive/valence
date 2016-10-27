# Copyright 2015 Lenovo
#
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

"""
Intel Pod Manager Driver vendor passthru methods
"""

from oslo_config import cfg
from oslo_log import log as logging
from ironic.drivers import base
from ironic import objects
import constants
from utils import http
import rsa_podm_adapter
import common
import math

confluent_opts = [
    cfg.StrOpt('ip',
               default='',
               help='the confluent server address'),
    cfg.StrOpt('user',
               default='',
               help='the confulent server username'),
    cfg.StrOpt('password',
               default='',
               help='the confulent server password'),
]

# as to the port of confluent, we may need to add it
CONF = cfg.CONF
CONF.register_opts(confluent_opts, group='confluent')

LOG = logging.getLogger(__name__)


class RSAPodmVendorPassthru(base.VendorInterface):
    """ passthru method entrance """

    def get_properties(self):
        return common.PODM_REQUIRED_PROPERTIES

    def validate(self, task, method, **kwargs):
        return common.parse_podm_driver_info(task.node)

    def vendor_passthru(self, task, **kwargs):
        pass

    def driver_vendor_passthru(self, context, method, **kwargs):
        """
        driver vendor passthru
        all subscribe actions are driver vendor passthru
        all pod manager management actions are driver vendor passthru
        """
        self.context = context
        functions_map = {
            # pod manager
            'manage_pod_manager': self.manage_pod_manager,
            'get_pod_manager_list': self.get_pod_manager_list,
            'unmanage_pod_manager': self.unmanage_exist_pod_manager,
            'inventory_pod_manager_resources':
                self.inventory_pod_manager_resources,
            'get_pod_inventory_status': self.get_pod_inventory_status,

            # chassis: Rack and Drawer
            'inventory_rsa_chassis': self.inventory_rsa_chassis,
            'get_rack_list': self.get_rack_list,
            'get_rack_info': self.get_rack_by_chassis_id,
            'get_drawer_list': self.get_drawer_list,
            'get_drawer_info': self.get_drawer_by_chassis_id,
            'get_rack_view': self.get_rack_view,

            # get pcieSwitch info
            'get_pcie_switch': self.get_pcie_switch_info,

            # computer system
            'get_computer_system_list': self.get_computer_system_list,
            'inventory_computer_system': self.inventory_computer_system,
            'get_computer_system_info':
                self.get_computer_system_details_info_by_id,
            'set_system_power_state': 1,

            # composed node
            'get_composed_node_list': self.get_composed_node_list,
            'inventory_composed_node': self.inventory_composed_node,
            'get_composed_node_info':
                self.get_composed_node_details_info_by_id,
            'set_node_power_state': self.set_composed_node_power_state,

            # ethernet switches
            'inventory_switch': self.inventory_ethernet_switches,
            'get_switch_list': self.get_ethernet_switch_list,
            'get_switch_info': self.get_ethernet_switch_info,

            # volumes
            'inventory_volumes': self.inventory_volumes,
            'get_volume_list': self.get_volume_list,
            'get_volume_info': self.get_volume_info,

            # storages (pcieswitch or target by pod_type)
            'inventory_storages': self.inventory_storages,
            'get_storage_list': self.get_storage_list,
            'get_storage_info': self.get_storage_info,

            # RMM
            'get_rmm_info': self.get_rmm_info,

            # Rack Manager
            'get_rack_manager_list': self.get_rack_manager_list,
            'get_rack_manager_info': self.get_rack_manager_info,
            'inventory_rack_manager': self.inventory_rack_manager,

            # Others
            'get_resource_summary': self.get_resource_usage_summary,
            'get_pod_manager_hardware_summary':
                self.get_pod_manager_hardware_summary,
            'get_rack_hardware_summary':
                self.get_rack_hardware_resource_summary,
        }
        return functions_map[method](context, **kwargs)

    #  --------- cache declare -------------------------------------  #

    # use for cache to protect from so much get operation from DB
    select_pod_managers = {}
    # use for cache to protect from so many generate operations of
    # PodManagerAPI class
    pod_manager_adapters = {}

    #  ---------- callable functions -------------------------------  #

    """
    summary
    """

    def get_resource_usage_summary(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        usage = dict()
        total_system_id_list = [system.id for system in
                                objects.ComputerSystem.list_by_pod(context,
                                                                   pod_id)]
        used_system_id_list = [node.computer_system_id for node in
                               objects.ComposedNode.list_by_pod(context,
                                                                pod_id)]

        for model in ['Disk', 'CPU', 'Memory']:
            for flag in ['total', 'used']:
                string = 'objects.%s.get_%s_sum_by_systems(context, ' \
                         '%s_system_id_list)' % (model,
                                                 model.lower(),
                                                 flag)
                usage[flag + '_' + model.lower()] = eval(string)

        return {'data': usage}

    def get_pod_manager_hardware_summary(self, context, **kwargs):
        pod_id = kwargs['pod_id']

        return {
            'data': {
                'Racks': len(
                    objects.RSAChassis
                        .list_by_pod_and_type(context,
                                              pod_id,
                                              constants.CHASSIS_TYPE_RACK)),
                'Drawer': len(
                    objects.RSAChassis
                        .list_by_pod_and_type(context,
                                              pod_id,
                                              constants.CHASSIS_TYPE_DRAWER)),
                'ComputerSystems': len(
                    objects.ComputerSystem.list_by_pod(context, pod_id)),
                # 'Storage': storage,
                'EthernentSwitchs': len(
                    objects.Switch.list_by_pod_id(context, pod_id)),
                'ComposedNodes': len(
                    objects.ComposedNode.list_by_pod(context, pod_id)),
                'Storages': len(
                    objects.Volume.list_by_pod_id(context, pod_id)),
            }
        }

    def get_rack_hardware_resource_summary(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        rack_id = kwargs['rack_id']
        return {'data': objects.RSAChassis.get_rack_resource(pod_id, rack_id,
                                                             context)}

    """
    Pod Manager functions
    """

    def manage_pod_manager(self, context, **kwargs):
        """ create a pod manager record in db"""
        pod_manager = objects.PodManager(context)
        pod_manager.name = kwargs['name']
        pod_manager.ipaddress = kwargs['ipaddress']
        pod_manager.username = kwargs['username']
        pod_manager.password = kwargs['password']
        pod_manager.description = kwargs['description']
        pod_manager.type = kwargs['type']
        pod_manager.url = 'https://%s' % kwargs['ipaddress']
        try:
            http.do_get_request(url=pod_manager.url)
            pod_manager.status = 'Online'
        except Exception:
            pod_manager.status = 'Offline'
        pod_manager.create()

    def unmanage_exist_pod_manager(self, context, **kwargs):
        pod_id = kwargs['pod_manager_id']
        objects.PodManager.destroy(pod_id, context)

    def get_pod_manager_list(self, context, **kwargs):
        """get pod manager list"""
        pod_manager_list = objects.PodManager.list(context)
        return {'data': map(lambda podm: podm.as_dict(), pod_manager_list)}

    def inventory_pod_manager_resources(self, context, **kwargs):
        """inventory all this pod_manager's resources in dependent order"""
        pod_id = kwargs['pod_id']
        pod_manager = objects.PodManager.get_by_id(context, pod_id)
        pod_manager.inventory_status = 'inventorying'
        pod_manager.save()

        try:
            self.inventory_rack_manager(context, pod_id=pod_id)
            self.inventory_rsa_chassis(context, pod_id=pod_id)
            self.inventory_computer_system(context, pod_id=pod_id)
            self.inventory_storages(context, pod_id=pod_id)
            self.inventory_volumes(context, pod_id=pod_id)
            self.inventory_composed_node(context, pod_id=pod_id)
            self.inventory_ethernet_switches(context, pod_id=pod_id)
        except Exception as ex:
            LOG.error(
                "refresh inventory pod manger: %s failed" % pod_manager.name)
            LOG.error(ex)
            pod_manager.inventory_status = 'failed'
            pod_manager.save()

        pod_manager.inventory_status = 'finished'
        pod_manager.save()

    def get_pod_inventory_status(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        return {'data': objects.PodManager.get_by_id(context,
                                                     pod_id).inventory_status}

    """
    RSA Chassis (Rack and Drawer) functions
    """

    def inventory_rsa_chassis(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        # Rack or Drawer or None(inventory all types)
        chassis_type = kwargs.get('chassis_type', None)
        # delete chassis
        objects.RSAChassis.destroy(pod_id, chassis_type, context)
        # get chassis from res pod manager
        adapter = self.__get_pod_manager_adapter(context, pod_id)
        chassis_list = adapter.get_chassis_list(chassis_type=chassis_type)
        # insert chassis info into DB
        map(lambda chassis_info: self.__synchronize_rsa_chassis(context,
                                                                pod_id,
                                                                chassis_info),
            chassis_list)

    def get_rack_list(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        chassis_list = objects.RSAChassis \
            .list_by_pod_and_type(context, pod_id,
                                  constants.CHASSIS_TYPE_RACK)
        return {'data': map(lambda x: x.as_dict(), chassis_list)}

    def get_rack_by_chassis_id(self, context, **kwargs):
        chassis_id = kwargs['chassis_id']
        return {'data': objects.RSAChassis.get_by_id(context,
                                                     chassis_id).as_dict()}

    def get_drawer_list(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        chassis_list = objects.RSAChassis \
            .list_by_pod_and_type(context, pod_id,
                                  constants.CHASSIS_TYPE_DRAWER)
        return {'data': map(lambda x: x.as_dict(), chassis_list)}

    def get_drawer_by_chassis_id(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        chassis_id = kwargs['chassis_id']
        chassis_info = objects.RSAChassis.get_by_id(context,
                                                    chassis_id).as_dict()
        # get rack id
        pod_manager_url = self.__get_pod_manager(context, pod_id).url
        rack_url = pod_manager_url + '/redfish/v1/Chassis/' + \
                   eval(chassis_info['location'])['Rack']
        rack_id = objects.RSAChassis.get_by_url(context, rack_url).id
        chassis_info['rack_id'] = rack_id
        # get computer systems
        chassis = chassis_info['url'].split('/')[-1]
        chassis_info[
            'computer_systems'] = objects.RSAChassis \
            .get_chassis_computer_systems(pod_id, chassis, chassis_id, context)
        return {'data': chassis_info}

    def get_rack_view(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        rack_id = kwargs['rack_id']
        rack_name = objects.RSAChassis.get_by_id(context, rack_id).name
        switch_list = self.get_ethernet_switch_list(context, pod_id=pod_id)[
            'data']
        switch_list = filter(lambda switch: rack_name in switch["location"],
                             switch_list)
        switch_list = map(self.__filter_switch, switch_list)
        drawer_list = self.get_drawer_list(context, pod_id=pod_id)['data']
        drawer_list = filter(lambda drawer: rack_name in drawer["location"],
                             drawer_list)
        drawer_list = map(self.__filter_drawer, drawer_list)
        drawer_list = sorted(drawer_list,
                             key=lambda drawer: int(drawer['ULocation'][0:2]),
                             reverse=True)
        if switch_list:
            drawer_list.insert(0, switch_list[0])
        return {'data': drawer_list}

    def get_pcie_switch_info(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        pcie = \
            objects.RSAChassis.list_by_pod_and_type(context, pod_id,
                                                    'RackMount')[
                0]
        return {'data': pcie.as_dict()}

    """
    Computer System functions
    """

    def get_computer_system_list(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        pod_type = self.__get_pod_manager(context, pod_id).type
        system_list = objects.ComputerSystem.list_by_pod(context, pod_id)
        data = map(
            lambda system: self.__filter_system_location(
                system) if pod_type != "INTEL-COMMON" else system.as_dict(),
            system_list)

        return {'data': data}

    def inventory_computer_system(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        # delete computer systems
        objects.ComputerSystem.destroy(pod_id, context)
        # get computer systems info from pod manager
        adapter = self.__get_pod_manager_adapter(context, pod_id)
        computer_systems = adapter.get_computer_system_list_info()
        # insert computer system info DB
        map(lambda system: self.__synchronize_computer_system(context, pod_id,
                                                              system),
            computer_systems)

    def get_computer_system_details_info_by_id(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        node_id = kwargs['system_id']
        system = objects.ComputerSystem.get_by_id(context, node_id)
        pod_manager_url = self.__get_pod_manager(context, pod_id).url
        # get chassis id by url
        pod_type = self.__get_pod_manager(context, pod_id).type
        if pod_type == "INTEL-COMMON":
            drawer_url = pod_manager_url + '/redfish/v1/Chassis/' + \
                         eval(system.location)['Chassis']
            rack_url = pod_manager_url + '/redfish/v1/Chassis/' + \
                       eval(system.location)['Rack']
            drawer_id = objects.RSAChassis.get_by_url(context, drawer_url).id
            rack_id = objects.RSAChassis.get_by_url(context, rack_url).id
            system = system.as_dict()
        else:
            drawer_id = \
                eval(objects.ComputerSystem.get_by_id(context,
                                                      node_id).location)[
                    "Chassis"]
            rack_id = \
                eval(objects.ComputerSystem.get_by_id(context,
                                                      node_id).location)[
                    "Rack"]
            system = self.__filter_system_location(system)
        system['drawer_id'] = drawer_id
        system['rack_id'] = rack_id
        system['cpus'] = objects.CPU.list_by_node_id(context, node_id)
        system['memorys'] = objects.Memory.list_by_node_id(context, node_id)
        system['disks'] = objects.Disk.list_by_node_id(context, node_id)
        system['interfaces'] = objects.Interface.list_by_node_id(context,
                                                                 node_id)
        system['composed_node'] = objects.ComposedNode.get_by_system_id(
            context, node_id)
        return {'data': system}

    def set_computer_system_power_state(self, context, **kwargs):
        computer_system_id = kwargs['system_id']
        state = kwargs['state']
        node_db = objects.ComputerSystem.get_by_id(context, computer_system_id)
        pod_manager = objects.PodManager.get_by_id(context, node_db.pod_id)
        podm = rsa_podm_adapter.get_podm_connection(context,
                                                    pod_manager.ipaddress,
                                                    pod_manager.username,
                                                    pod_manager.password)
        if podm.set_rsa_node_power_state(path=node_db.uri, state=state):
            node_db.power_state = state
            node_db.save()

    """
    Composed Node functions
    """

    def get_composed_node_list(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        pod_type = self.__get_pod_manager(context, pod_id).type
        node_list = objects.ComposedNode.list_by_pod(context, pod_id)
        node_list_info = []
        for node in node_list:
            system = objects.ComputerSystem.get_by_id(context,
                                                      node.computer_system_id)
            system = self.__filter_system_location(
                system) if pod_type != "INTEL-COMMON" else system.as_dict()
            info = dict(system, **node.as_dict())
            node_list_info.append(info)
        return {'data': node_list_info}

    def inventory_composed_node(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        # delete composed nodes
        objects.ComposedNode.destroy(pod_id, context)
        # get composed nodes info from pod manager
        adapter = self.__get_pod_manager_adapter(context, pod_id)
        composed_nodes = adapter.get_composed_node_list_info()
        # insert composed node info DB
        map(lambda node: self.__synchronize_composed_node(context, pod_id,
                                                          node),
            composed_nodes)

    def get_composed_node_details_info_by_id(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        node_id = kwargs['node_id']
        node = objects.ComposedNode.get_by_id(context, node_id)
        # get system info
        system = \
            self.get_computer_system_details_info_by_id(
                context, pod_id=pod_id, system_id=node.computer_system_id)
        system['data']['computer_system_name'] = system['data']['name']
        # get volume info
        volume_list = map(lambda volume_id:
                          objects.Volume.get_by_id(context,
                                                   volume_id).as_dict(),
                          eval(node.volume_id))
        system['data']['volume'] = volume_list
        return {'data': dict(system['data'], **node.as_dict())}

    def set_composed_node_power_state(self, context, **kwargs):
        node_id = kwargs['node_id']
        state = kwargs['state']
        node_db = objects.ComputerSystem.get_by_id(context, node_id)
        adapter = self.__get_pod_manager_adapter(context, node_db.pod_id)
        if adapter.set_rsa_node_power_state(path=node_db.uri, state=state):
            node_db.power_state = state
            node_db.save()

    """
    ethernet Switches functions
    """

    def get_ethernet_switch_list(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        switch_list = objects.Switch.list_by_pod_id(context, pod_id)
        return {'data': map(lambda switch: switch.as_dict(), switch_list)}

    def get_ethernet_switch_info(self, context, **kwargs):
        switch_id = kwargs['switch_id']
        switch = objects.Switch.get_by_id(context, switch_id).as_dict()
        return {'data': switch}

    def inventory_ethernet_switches(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        # delete switches
        objects.Switch.destroy(pod_id, context)
        # get switch info from pod manager adapter
        adapter = self.__get_pod_manager_adapter(context, pod_id)
        switch_list = adapter.get_ethernet_switches_list_info()
        # insert switch into DB
        map(lambda switch: self.__synchronize_switch(context, pod_id, switch),
            switch_list)

    """
    Volumes functions
    """

    def get_volume_list(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        volume_list = objects.Volume.list_by_pod_id(context, pod_id)
        data = map(
            lambda volume: self.get_volume_info(context, volume_id=volume.id)[
                'data'], volume_list)
        return {'data': data}

    def get_volume_info(self, context, **kwargs):
        volume_id = kwargs['volume_id']
        volume = objects.Volume.get_by_id(context, volume_id).as_dict()
        # get storage_name
        pod_type = self.__get_pod_manager(context, volume['pod_id']).type
        storage_model = objects.PCIeSwitch
        try:
            volume['storage_name'] = storage_model.get_by_id(context, volume[
                'controller_id']).name
        except Exception:  # TODO wait for pcieSwitch-volume relationship
            volume['storage_name'] = ''
        # get composed_node
        volume["composed_node"] = objects.ComposedNode.get_by_volume_id(
            context, volume_id)
        return {'data': volume}

    def inventory_volumes(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        # delete volumes
        objects.Volume.destroy(pod_id, context)
        # get volume info from pod manager adapter
        adapter = self.__get_pod_manager_adapter(context, pod_id)
        volume_list = adapter.get_volume_list_info()
        # insert volume into DB
        map(lambda volume: self.__synchronize_volume(context, pod_id, volume),
            volume_list)

    """
    Storage functions
    """

    def get_storage_list(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        pod_type = self.__get_pod_manager(context, pod_id).type
        storage_model = objects.PCIeSwitch
        storage_list = storage_model.list_by_pod(context, pod_id)
        storage_list = map(lambda target: target.as_dict(), storage_list)
        data = {"storage_name": storage_model.__name__,
                "storage_list": storage_list}
        return {'data': data}

    def get_storage_info(self, context, **kwargs):
        storage_id = kwargs['storage_id']
        pod_id = kwargs['pod_id']
        pod_type = self.__get_pod_manager(context, pod_id).type
        storage_model = objects.PCIeSwitch
        storage = storage_model.get_by_id(context, storage_id).as_dict()
        return {'data': storage}

    def inventory_storages(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        pod_type = self.__get_pod_manager(context, pod_id).type
        storage_model = objects.PCIeSwitch
        # delete storages
        storage_model.destroy(pod_id, context)
        # get storage info from pod manager adapter
        adapter = self.__get_pod_manager_adapter(context, pod_id)
        storage_list = adapter.get_storage_list_info()
        # insert storage into DB
        map(lambda storage: self.__synchronize_storage(context, pod_id,
                                                       storage), storage_list)

    """
    RMM functions
    """

    def get_rmm_info(self, context, **kwargs):
        return {'data': ""}

    """
    Manager functions
    """

    def get_rack_manager_list(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        manager_list = objects.Manager.list_by_pod(context, pod_id)
        return {'data': map(lambda manager: manager.as_dict(), manager_list)}

    def get_rack_manager_info(self, context, **kwargs):
        manager_id = kwargs['manager_id']
        manager = objects.Manager.get_by_id(context, manager_id).as_dict()
        # TODO return computer_systems/rsa_chassis in manager.
        return {'data': manager}

    def inventory_rack_manager(self, context, **kwargs):
        pod_id = kwargs['pod_id']
        # delete managers
        objects.Manager.destroy(pod_id, context)
        # get managers info from pod manager
        adapter = self.__get_pod_manager_adapter(context, pod_id)
        managers = adapter.get_manager_list_info()
        # insert manager info DB
        map(lambda manager: self.__synchronize_manager(context, pod_id,
                                                       manager), managers)

    """
    Others functions
    """

    def get_resource_summary_usage(self, context, **kwargs):
        return {'data': ""}

    # ------------- helper functions ------------------------------- #

    def __get_pod_manager(self, context, pod_manager_id):
        # deal with cache mechanism
        if pod_manager_id in self.select_pod_managers:
            return self.select_pod_managers[pod_manager_id]
        else:
            pod_manager = objects.PodManager.get_by_id(context, pod_manager_id)
            self.select_pod_managers[pod_manager_id] = pod_manager
            return pod_manager

    def __get_pod_manager_adapter(self, context, pod_manager_id):
        # deal with cache mechanism
        if pod_manager_id in self.pod_manager_adapters:
            return self.pod_manager_adapters[pod_manager_id]
        else:
            pod_manager = self.__get_pod_manager(context, pod_manager_id)
            pod_manager_adapter = \
                rsa_podm_adapter.get_podm_connection(
                    context, ip=pod_manager.ipaddress,
                    user=pod_manager.username, passwd=pod_manager.password)
            self.pod_manager_adapters[pod_manager_id] = pod_manager_adapter
            return pod_manager_adapter

    def __get_volume_ids(self, context, pod_manager_url, volume_list):
        volume_ids = []
        for item in volume_list:
            volume_url = pod_manager_url + item["@odata.id"]
            volume_id = objects.Volume.get_by_url(context, volume_url).id
            volume_ids.append(volume_id)
        return str(volume_ids)

    def __filter_drawer(self, db_drawer):
        drawer = dict()
        drawer['id'] = db_drawer['id']
        drawer['type'] = db_drawer['type']
        drawer['model'] = db_drawer['model']
        drawer['ULocation'] = eval(db_drawer['location'])['ULocation']
        drawer['UHeight'] = eval(db_drawer['location'])['UHeight']
        drawer['UWidth'] = eval(db_drawer['location'])['UWidth']
        drawer_name = db_drawer['url'].split('/')[-1]
        drawer['computer_systems'] = objects.RSAChassis \
            .get_chassis_computer_systems(db_drawer['pod_id'],
                                          drawer_name,
                                          drawer['id'],
                                          self.context)
        return drawer

    def __filter_switch(self, db_switch):
        switch = dict()
        switch['id'] = db_switch['id']
        switch['name'] = db_switch['name']
        return switch

    def __filter_system_location(self, system):
        location = eval(system.location)
        location['Rack'] = objects.RSAChassis.get_by_id(self.context,
                                                        location['Rack']).name
        system.location = location
        return system.as_dict()

    def __synchronize_computer_system(self, context, pod_id, system_info):
        """
        refresh db node record: update or create

        :type context:
        :type pod_id: int
        :param system_info: computer system info from pod manager

        :return: db_node object
        """
        pod_manager_url = self.__get_pod_manager(context, pod_id).url
        try:
            manager_url = pod_manager_url + \
                          system_info["Links"]["ManagedBy"][0]["@odata.id"]
            chassis_url = pod_manager_url + system_info["Links"]["Chassis"][0][
                "@odata.id"]
        except Exception:
            manager_url = ''
            chassis_url = ''
        system_db = objects.ComputerSystem(context)
        system_db.type = system_info['SystemType']
        system_db.uuid = system_info['UUID']
        system_db.name = system_info['Name']
        system_db.description = system_info['Description']
        system_db.model = system_info['Model']
        system_db.hostname = system_info['HostName']
        system_db.power_state = system_info['PowerState']
        system_db.status = system_info['Status']
        pod_type = self.__get_pod_manager(context, pod_id).type
        if pod_type == "INTEL-COMMON":
            system_db.location = system_info['Oem']['Lenovo:RackScale'][
                'Location']
        else:
            # TODO system's location store chassis/rack id & use id
            # to search systems in rack/drawer later
            chassis = objects.RSAChassis.get_by_url(context, chassis_url)
            rack = \
                eval(objects.RSAChassis.get_by_id(context,
                                                  chassis.id).location)[
                    "Rack"]
            rack_url = pod_manager_url + "/redfish/v1/Chassis/" + rack
            rack_id = objects.RSAChassis.get_by_url(context, rack_url).id
            system_location = int(
                system_info['Oem']['Lenovo:RackScale']['SystemLocation'])
            system_location = 14 if system_location % 14 == 0 \
                else system_location % 14
            chassis_location = int(
                filter(str.isdigit, str(eval(chassis.location)['ULocation'])))
            ULocation = chassis_location + int(
                math.floor((system_location + 1) / 2))
            system_db.location = {"Chassis": chassis.id, "Rack": rack_id,
                                  "ULocation": ULocation, "UHeight": "",
                                  "UWidth": "",
                                  "SystemLocation": system_location}
        system_db.pod_id = pod_id
        try:
            system_db.manager_id = objects.Manager.get_by_url(context,
                                                              manager_url).id
        except Exception:
            system_db.manager_id = 0
        system_db.url = pod_manager_url + system_info['@odata.id']
        system_db.asset_tag = system_info['AssetTag']
        system_db.indicator_led = system_info['IndicatorLED']
        system_db.asset_tag = system_info['AssetTag']
        system_db.bios_version = system_info['BiosVersion']
        system_db.sku = system_info['SKU']
        system_db.manufacturer = system_info['Manufacturer']
        system_db.serial_number = system_info['SerialNumber']
        system_db.part_number = system_info['PartNumber']
        system_db.create()

        map(lambda cpu: self.__insert_cpu_info(
            context, cpu, system_db.id), system_info['cpus'])
        map(lambda memory: self.__insert_memory_info(
            context, memory, system_db.id), system_info['memorys'])
        map(lambda disk: self.__insert_disk_info(
            context, disk, system_db.id), system_info['disks'])
        map(lambda interface: self.__insert_interface_info(
            context, interface, system_db.id), system_info['interfaces'])

    def __synchronize_composed_node(self, context, pod_id, node_info):
        pod_type = self.__get_pod_manager(context, pod_id).type
        pod_manager_url = self.__get_pod_manager(context, pod_id).url
        computer_system_url = pod_manager_url + \
                              node_info['Links']['ComputerSystem']['@odata.id']
        volume_list = node_info["Links"][
            "LocalDrives"] if pod_type == "INTEL-COMMON" else \
            node_info['Oem']['Lenovo:RackScale']['ComposedLogicalDrives']

        node_db = objects.ComposedNode(context)
        node_db.name = node_info['Name']
        node_db.description = node_info['Description']
        node_db.url = pod_manager_url + node_info['@odata.id']
        node_db.computer_system_id = \
            objects.ComputerSystem.get_by_url(context, computer_system_url).id
        node_db.volume_id = self.__get_volume_ids(context, pod_manager_url,
                                                  volume_list)
        node_db.pod_id = pod_id
        node_db.create()

    def __insert_cpu_info(self, context, cpu_info, computer_system_id):
        cpu_db = objects.CPU(context)
        cpu_db.computer_system_id = computer_system_id
        cpu_db.name = cpu_info['Name']
        cpu_db.model = cpu_info['Model']
        cpu_db.speed_mhz = float(cpu_info['MaxSpeedMHz'])
        cpu_db.total_cores = cpu_info['TotalCores']
        cpu_db.total_threads = cpu_info['TotalThreads']
        cpu_db.processor_type = cpu_info['ProcessorType']
        cpu_db.processor_architecture = cpu_info['ProcessorArchitecture']
        cpu_db.instruction_set = cpu_info['InstructionSet']
        cpu_db.manufacturer = cpu_info['Manufacturer']
        cpu_db.create()

    def __insert_memory_info(self, context, memory_info, computer_system_id):
        memory_db = objects.Memory(context)
        memory_db.computer_system_id = computer_system_id
        memory_db.name = memory_info['Name']
        memory_db.device_type = memory_info['DimmDeviceType']
        memory_db.capacity_mb = memory_info['CapacityMiB']
        memory_db.speed_mhz = memory_info['OperatingSpeedMHz']
        memory_db.serial_number = memory_info['SerialNumber']
        memory_db.part_number = memory_info['PartNumber']
        memory_db.manufacturer = memory_info['Manufacturer']
        memory_db.create()

    def __insert_disk_info(self, context, disk_info, computer_system_id):
        disk_db = objects.Disk(context)
        disk_db.computer_system_id = computer_system_id
        disk_db.type = disk_info['Interface']  # SATA or SAS of PCIe
        disk_db.model = disk_info['Model']
        disk_db.size_gb = disk_info['CapacityGiB']
        disk_db.serial_number = disk_info['SerialNumber']
        disk_db.create()

    def __insert_interface_info(self, context, interface_info,
                                computer_system_id):
        interface_db = objects.Interface(context)
        interface_db.computer_system_id = computer_system_id
        interface_db.name = interface_info['Name']
        interface_db.description = interface_info['Description']
        interface_db.mac_address = interface_info['MACAddress']
        interface_db.ip_address = interface_info['IPv4Addresses'][0]['Address']
        interface_db.status = interface_info['Status']
        interface_db.create()

    def __synchronize_switch(self, context, pod_id, switch_info):
        pod_manager_url = self.__get_pod_manager(context, pod_id).url
        switch_db = objects.Switch(context)
        switch_db.pod_id = pod_id
        switch_db.name = switch_info["Name"]
        switch_db.description = switch_info["Description"]
        switch_db.url = pod_manager_url + switch_info["@odata.id"]
        switch_db.manufacturer = switch_info["Manufacturer"]
        switch_db.manufactueing_date = switch_info["ManufacturingDate"]
        switch_db.model = switch_info["Model"]
        switch_db.serial_number = switch_info["SerialNumber"]
        switch_db.part_number = switch_info["PartNumber"]
        switch_db.firmware_name = switch_info["FirmwareName"]
        switch_db.firmware_version = switch_info["FirmwareVersion"]
        switch_db.status = switch_info["Status"]
        switch_db.location = switch_info['Oem']['Lenovo:RackScale']['Location']
        switch_db.create()
        return switch_db

    def __synchronize_rsa_chassis(self, context, pod_id, chassis_info):
        chassis_db = objects.RSAChassis(context)
        pod_type = self.__get_pod_manager(context, pod_id).type
        vendor = 'Lenovo' if pod_type == "INTEL-COMMON" else 'Intel'
        uuid = chassis_info["Oem"][vendor + ":RackScale"]["UUID"]
        pod_manager_url = self.__get_pod_manager(context, pod_id).url
        try:
            manager_url = pod_manager_url + \
                          chassis_info["Links"]["ManagedBy"][0]["@odata.id"]
            chassis_db.manager_id = objects.Manager.get_by_url(context,
                                                               manager_url).id
        except Exception:
            chassis_db.manager_id = 0
        chassis_db.type = chassis_info["ChassisType"]
        chassis_db.uuid = uuid
        chassis_db.url = pod_manager_url + chassis_info["@odata.id"]
        if pod_type == "INTEL-COMMON":
            chassis_db.location = chassis_info['Oem']['Lenovo:RackScale'][
                'Location']
        else:
            Rack = chassis_info['Oem']['Intel:RackScale']['Location'][
                "ParentId"]
            try:
                ULocation = \
                    chassis_info['Oem']['Lenovo:RackScale']['Location'][
                        "LowerUnit"] + ' U'
                UHeight = chassis_info['Oem']['Lenovo:RackScale']['Location'][
                              "Height"] + ' U'
            except Exception:
                ULocation = ""
                UHeight = ""
            chassis_db.location = {"ULocation": ULocation, "UWidth": "",
                                   "Rack": Rack, "UHeight": UHeight}
        chassis_db.name = chassis_info["Name"]
        chassis_db.pod_id = pod_id
        chassis_db.description = chassis_info["Description"]
        chassis_db.manufacturer = chassis_info["Manufacturer"]
        chassis_db.model = chassis_info["Model"]
        chassis_db.sku = chassis_info["SKU"]
        chassis_db.asset_tag = chassis_info["AssetTag"]
        chassis_db.serial_number = chassis_info["SerialNumber"]
        chassis_db.part_number = chassis_info["PartNumber"]
        chassis_db.indicator_led = chassis_info["IndicatorLED"]
        chassis_db.status = chassis_info["Status"]
        chassis_db.create()
        return chassis_db

    def __synchronize_volume(self, context, pod_id, volume_info):
        """
        refresh db volume record: update or create

        :param context:
        :param volume_info: node info from pod manager

        :return: volume_db
        """
        pod_manager_url = self.__get_pod_manager(context, pod_id).url
        pod_type = self.__get_pod_manager(context, pod_id).type

        volume_db = objects.Volume(context)
        volume_db.url = pod_manager_url + volume_info['@odata.id']
        volume_db.name = volume_info["Name"]
        volume_db.description = volume_info["Description"]
        volume_db.mode = volume_info["Mode"] if "Mode" in volume_info else \
            volume_info["Model"]
        volume_db.size_GB = volume_info[
            "CapacityGiB"] if "CapacityGiB" in volume_info \
            else volume_info["CapacityBytes"] / 10 ** 9
        volume_db.pod_id = pod_id
        volume_db.type = ''
        if pod_type == "INTEL-COMMON":
            storage_url = pod_manager_url + volume_info['Links']['Targets'][0][
                '@odata.id']
            volume_db.controller_id = \
                objects.RemoteTarget.get_by_url(context, storage_url).id
        else:
            volume_db.controller_id = 0
        volume_db.create()
        return volume_db.as_dict()

    def __synchronize_storage(self, context, pod_id, storage_info):
        """
        refresh db target record: update or create

        :param context:
        :param target_info: node info from pod manager

        :return: target_db1
        """
        pod_type = self.__get_pod_manager(context, pod_id).type
        storage_model = objects.PCIeSwitch
        pod_manager_url = self.__get_pod_manager(context, pod_id).url
        storage_db = storage_model(context)
        storage_db.url = pod_manager_url + storage_info['@odata.id']
        storage_db.name = storage_info["Name"]
        storage_db.pod_id = pod_id
        if storage_model == objects.RemoteTarget:
            storage_db.address = storage_info["Address"][0]["iSCSI"][
                "TargetPortalIP"]
            storage_db.port = storage_info["Address"][0]["iSCSI"][
                "TargetPortalPort"]
            storage_db.status = storage_info["Status"]
        else:
            storage_db.description = storage_info["Description"]
            storage_db.status = storage_info["Status"]
            storage_db.type = storage_info["ChassisType"]
        storage_db.create()
        return storage_db.as_dict()

    def __synchronize_manager(self, context, pod_id, manager_info):
        """
        refresh db manager record: update or create

        :param context:
        :param manager_info: node info from pod manager

        :return: manager_db
        """
        pod_manager_url = self.__get_pod_manager(context, pod_id).url

        manager_db = objects.Manager(context)
        manager_db.url = pod_manager_url + manager_info['@odata.id']
        manager_db.name = manager_info["Name"]
        manager_db.type = manager_info["ManagerType"]
        manager_db.description = manager_info["Description"]
        manager_db.model = manager_info["Model"]
        manager_db.firmware_version = manager_info['FirmwareVersion']
        manager_db.graphical_console = manager_info['GraphicalConsole']
        manager_db.serial_console = manager_info['SerialConsole']
        manager_db.command_shell = manager_info['CommandShell']
        manager_db.status = manager_info['Status']
        manager_db.pod_id = pod_id
        manager_db.uuid = manager_info['UUID']
        manager_db.create()
        return manager_db.as_dict()
