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

from openstack_dashboard.api import base
from horizon.utils.memoized import memoized  # noqa
from openstack_dashboard.api.ironic import driver_vendor_call, extract_driver_dict_result
import re
# rsa based on ironic
#from openstack_dashboard.api.ironic import *


class Event(base.APIDictWrapper):
    _attrs = ['time', 'message', 'eventtype', 'target']


class Blade(base.APIDictWrapper):
    _attrs = ['name', 'description', 'hostname', 'power', 'health', 'model']


class VirtualDisk(base.APIDictWrapper):
    _attrs = [
        'name',
        'description',
        'status',
        'health',
        'type',
        'mode',
        'capacity',
        'image',
     'bootable']


class Rack(base.APIDictWrapper):
    _attrs = [
        'name',
        'description',
        'status',
        'health',
        'type',
        'mode',
        'capacity',
        'image',
     'bootable']


class ComposedServer(base.APIDictWrapper):
    _attrs = [
        'name',
        'description',
        'power',
        'composedstate',
        'model',
     'assettag']


class Drawer(base.APIDictWrapper):
    _attrs = ['name', 'description', 'model', 'status', 'location']


class PodManager(base.APIDictWrapper):
    _attrs = [
        'name',
        'description',
        'username',
        'password',
        'status',
        'ip',
     'link']

class EthernetSwitch(base.APIDictWrapper):
    _attrs = ['name', 'status', 'description', 'model', 'health', 'location']

class PcieSwitch(base.APIDictWrapper):
    """Pcie Switches in dict, for xClarity driver, we put the detail info in extra field"""

    _attrs = ['name', 'status', 'description', 'model', 'health', 'location']
    '''
    _attrs = ['name', 'vendor_name', 'uuid', 'power_state', 'product_name', 'management_ip', 'cpu', 'memory', 'disk', 'nic',
              'location', 'physical_uuid', 'hasOS', 'assigned', 'applied', 'project', 'provision_state', 'readyCheck',
              'mac_addresses', 'console_user', 'console_passwd', 'firmware','fodkey', 'access_state','hypervisor', 'hypervisor_type']
    '''

    '''
    @property
    def name(self):
        return self.get('name','')

    @property
    def vendor_name(self):
        return self._apidict['extra'].get('vendor_name','')

    @property
    def product_name(self):
        return self._apidict['extra'].get('product_name','')
    @property
    def management_ip(self):
        return self._apidict['extra'].get('management_ip','')

    #for these cpu
    @property
    def cpu(self):
        return self._apidict['extra'].get('cpu',[])
    @property
    def memory(self):
        return self._apidict['extra'].get('memory',[])
    @property
    def disk(self):
        return self._apidict['extra'].get('disk',[])
    @property
    def firmware(self):
        return self._apidict['extra'].get('firmware',[])
    @property
    def fodkey(self):
        return self._apidict['extra'].get('fodkey',[])
    @property
    def nic(self):
        return self._apidict['extra'].get('nic',[])
    @property
    def location(self):
        return self._apidict['extra'].get('location','')
    @property
    def physical_uuid(self):
        return self._apidict['extra'].get('physical_uuid','')
    @property
    def hasOS(self):
        return self._apidict['extra'].get('hasOS','')
    @property
    def assigned(self):
        return self._apidict['extra'].get('assigned','')
    @property
    def applied(self):
        return self._apidict['extra'].get('applied','')
    @property
    def project(self):
        return self._apidict['extra'].get('project','')
    @property
    def access_state(self):
        return self._apidict['extra'].get('access_state','')
    '''

    '''
    @property
    def uuid(self):
        return self._apidict.get('uuid','')

    @property
    def hypervisor(self):
        return self._apidict.get('hypervisor','')

    @property
    def hypervisor_type(self):
        return self._apidict.get('hypervisor_type','')


    @property
    def power_state(self):
        return self._apidict.get('power_state','')

    @property
    def driver(self):
        return self._apidict.get('driver','')

    @property
    def provision_state(self):
        """move the ready status of lxca driver into specs"""
        return self._apidict.get('provision_state','')

    '''
    '''
    @property
    def readyCheck(self):
        return self._apidict['extra'].get('readyCheck',{})
    @property
    def mac_addresses(self):
        return self._apidict['extra'].get('mac_addresses',[])
    @property
    def console_user(self):
        return self._apidict['extra'].get('console_user','')

    @property
    def console_passwd(self):
        return self._apidict['extra'].get('console_passwd','')

    @property
    def console_port(self):
        return self._apidict['extra'].get('console_port','')
    '''

class RackManager(base.APIDictWrapper):
    _attrs = ['name', 'description', 'model', 'status', 'location']

@memoized
def pcie_switches_list(request, pod_id, refresh=False, project=''):
    kwargs = {
                #'refresh': str(refresh),
                'project': project,
                'pod_id': pod_id
            }
    switches_list = []
    try:
        if refresh == False:
            driver_vendor_result = driver_vendor_call(
                'pod_manager', 'get_switch_list', **kwargs)
        else:
            driver_vendor_result = driver_vendor_call(
                'pod_manager', 'inventory_switch', **kwargs)
        driver_list_result = extract_driver_dict_result(driver_vendor_result)
        for i, x in enumerate(driver_list_result):
            driver_list_result[i]['status'] = eval(x['status'])['Health']
            if x.has_key('location'):
                if 'Rack' in eval(x['location']):
                    driver_list_result[i]['rack'] = eval(x['location'])['Rack']
                if 'ULocation' in eval(x['location']):
                    driver_list_result[i]['location'] = eval(x['location'])[
                                                            'ULocation']
            if driver_list_result[i].has_key('rack') and driver_list_result[i].has_key('location'):
                driver_list_result[i]['location_summary'] = driver_list_result[
                    i]['rack'] + ' : ' + driver_list_result[i]['location']
            else:
                driver_list_result[i]['location_summary'] = ''


    except:
        import traceback
        traceback.print_exc()
        driver_list_result = [
            {'name': u'IO Module 01', 'id': '1', 'status': 'normal',
             'description': 'blablabla', 'model': 'xt2039', 'health': 'good',
             'location': '12U', 'rack': 'rack001', 'partnumber': '69Y1932',
             'serialnumber': 'Y250NY21E026', 'ip_addr': '10.240.211.161'},
            {'name': u'IO Module 02', 'id': '2', 'status': 'normal',
             'description': 'blablabla', 'model': 'xt2039', 'health': 'good',
             'location': '11U', 'rack': 'rack003', 'partnumber': '69Y1925',
             'serialnumber': 'S250NY21E023', 'ip_addr': '10.240.211.10'},
            {'name': u'IO Module 03', 'id': '3', 'status': 'normal',
             'description': 'blablabla', 'model': 'xt2039', 'health': 'good',
             'location': '10U', 'rack': 'rack006', 'partnumber': '69Y1000',
             'serialnumber': 'Y250NY21E003', 'ip_addr': '10.240.211.12'},
            {'name': u'IO Module 04', 'id': '4', 'status': 'normal',
             'description': 'blablabla', 'model': 'xt2039', 'health': 'good',
             'location': '9U', 'rack': 'rack006', 'partnumber': '69Y0003',
             'serialnumber': 'Y250NY21E011', 'ip_addr': '10.240.211.1'},
            {'name': u'IO Module 05', 'id': '5', 'status': 'normal',
             'description': 'blablabla', 'model': 'xt2039', 'health': 'good',
             'location': '8U', 'rack': 'rack006', 'partnumber': '69Y1932',
             'serialnumber': 'Y250NY21E032', 'ip_addr': '10.240.211.15'},
            {'name': u'IO Module 06', 'id': '6', 'status': 'normal',
             'description': 'blablabla', 'model': 'xt2039', 'health': 'good',
             'location': '7U', 'rack': 'rack006', 'partnumber': '69Y0932',
             'serialnumber': 'Y250NY21E066', 'ip_addr': '10.240.211.16'}]
    for data in driver_list_result:
        pcie_switch = PcieSwitch(data)
        switches_list.append(pcie_switch)

    return switches_list

@memoized
def ethernet_switches_list(request, pod_id, refresh=False, project=''):
    kwargs = {
                #'refresh': str(refresh),
                'project': project,
                'pod_id': pod_id
            }
    switches_list = []
    try:
        if refresh == False:
            driver_vendor_result = driver_vendor_call(
                'pod_manager', 'get_switch_list', **kwargs)
        else:
            driver_vendor_result = driver_vendor_call(
                'pod_manager', 'inventory_switch', **kwargs)
        driver_list_result = extract_driver_dict_result(driver_vendor_result)
        for i, x in enumerate(driver_list_result):
            driver_list_result[i]['status'] = eval(x['status'])['Health']
            if x.has_key('location'):
                if 'Rack' in eval(x['location']):
                    driver_list_result[i]['rack'] = eval(x['location'])['Rack']
                if 'ULocation' in eval(x['location']):
                    driver_list_result[i]['location'] = eval(x['location'])[
                                                            'ULocation']
            if driver_list_result[i].has_key('rack') and driver_list_result[i].has_key('location'):
                driver_list_result[i]['location_summary'] = driver_list_result[
                    i]['rack'] + ' : ' + driver_list_result[i]['location']
            else:
                driver_list_result[i]['location_summary'] = ''
    except:
        import traceback
        traceback.print_exc()
        driver_list_result = [
            {'name': u'IO Module 01', 'id': '1', 'status': 'normal',
             'description': 'blablabla', 'model': 'xt2039', 'health': 'good',
             'location': '12U', 'rack': 'rack001', 'partnumber': '69Y1932',
             'serialnumber': 'Y250NY21E026', 'ip_addr': '10.240.211.161'},
            {'name': u'IO Module 02', 'id': '2', 'status': 'normal',
             'description': 'blablabla', 'model': 'xt2039', 'health': 'good',
             'location': '11U', 'rack': 'rack003', 'partnumber': '69Y1925',
             'serialnumber': 'S250NY21E023', 'ip_addr': '10.240.211.10'},
            {'name': u'IO Module 03', 'id': '3', 'status': 'normal',
             'description': 'blablabla', 'model': 'xt2039', 'health': 'good',
             'location': '10U', 'rack': 'rack006', 'partnumber': '69Y1000',
             'serialnumber': 'Y250NY21E003', 'ip_addr': '10.240.211.12'},
            {'name': u'IO Module 04', 'id': '4', 'status': 'normal',
             'description': 'blablabla', 'model': 'xt2039', 'health': 'good',
             'location': '9U', 'rack': 'rack006', 'partnumber': '69Y0003',
             'serialnumber': 'Y250NY21E011', 'ip_addr': '10.240.211.1'},
            {'name': u'IO Module 05', 'id': '5', 'status': 'normal',
             'description': 'blablabla', 'model': 'xt2039', 'health': 'good',
             'location': '8U', 'rack': 'rack006', 'partnumber': '69Y1932',
             'serialnumber': 'Y250NY21E032', 'ip_addr': '10.240.211.15'},
            {'name': u'IO Module 06', 'id': '6', 'status': 'normal',
             'description': 'blablabla', 'model': 'xt2039', 'health': 'good',
             'location': '7U', 'rack': 'rack006', 'partnumber': '69Y0932',
             'serialnumber': 'Y250NY21E066', 'ip_addr': '10.240.211.16'}]
    for data in driver_list_result:
        pcie_switch = PcieSwitch(data)
        switches_list.append(pcie_switch)

    return switches_list

@memoized
def drawers_list(request, pod_id, refresh=False, project=''):
    kwargs = {
                #'refresh': str(refresh),
                #'project':project,
                'pod_id': pod_id,
                #'chassis_type': 'Drawer'
            }
    drawers_list = []
    try:
        if refresh == False:
            driver_vendor_result = driver_vendor_call(
                'pod_manager', 'get_drawer_list', **kwargs)
        else:
            driver_vendor_result = driver_vendor_call(
                'pod_manager', 'inventory_rsa_chassis', **kwargs)
        driver_list_result = extract_driver_dict_result(driver_vendor_result)
        for i, x in enumerate(driver_list_result):
            driver_list_result[i]['status_2'] = eval(x['status'])['Health']
            if 'Rack' in eval(x['location']):
                driver_list_result[i]['rack'] = eval(x['location'])['Rack']
            if 'ULocation' in eval(x['location']):
                driver_list_result[i]['location'] = eval(x['location'])[
                                                         'ULocation']
            if driver_list_result[i].has_key('rack') and driver_list_result[i].has_key('location'):
                driver_list_result[i]['location_summary'] = driver_list_result[
                    i]['rack'] + ' : ' + driver_list_result[i]['location']
            else:
                driver_list_result[i]['location_summary'] = ''

    except:
        import traceback
        traceback.print_exc()
        driver_list_result = [
            {'name': u'drawer001', 'id': '1', 'description': 'test001',
             'model': '8721', 'location': '32U', 'status': 'normal',
             'uuid': '1726g21fg21y2t710', 'rack': 'rack001'},
            {'name': u'drawer002', 'id': '2', 'description': 'test002',
             'model': '8721', 'location': '1U', 'status': 'normal',
             'uuid': '1726g21fg21y1th12', 'rack': 'rack001'},
            {'name': u'drawer003', 'id': '10', 'description': 'test003',
             'model': '8721', 'location': '20U', 'status': 'normal',
             'uuid': '17d6g21fg21y1th13', 'rack': 'rack003'},
            {'name': u'drawer004', 'id': '4', 'description': 'test004',
             'model': '8721', 'location': '19U', 'status': 'normal',
             'uuid': '1726g11fg21y1th12', 'rack': 'rack003'},
            {'name': u'drawer005', 'id': '5', 'description': 'test005',
             'model': '8721', 'location': '11U', 'status': 'normal',
             'uuid': '1726g010g01y1th12', 'rack': 'rack006'}, ]
    for data in driver_list_result:
        drawer = Drawer(data)
        drawers_list.append(drawer)
    return drawers_list

@memoized
def rack_managers_list(request, pod_id, refresh=False, project=''):
    kwargs = {
                'pod_id': pod_id,
            }
    rack_managers_list = []
    try:
        if refresh == False:
            driver_vendor_result = driver_vendor_call(
                'pod_manager', 'get_rack_manager_list', **kwargs)
        else:
            driver_vendor_result = driver_vendor_call(
                'pod_manager', 'inventory_rack_manager', **kwargs)
        driver_list_result = extract_driver_dict_result(driver_vendor_result)
        for i, x in enumerate(driver_list_result):
            driver_list_result[i]['status_2'] = eval(x['status'])['Health']
            driver_list_result[i]['uuid'] = driver_list_result[i]['uuid'][-12:]
            if x.has_key('location'):
                if 'Rack' in eval(x['location']):
                    driver_list_result[i]['rack'] = eval(x['location'])['Rack']
                if 'ULocation' in eval(x['location']):
                    driver_list_result[i]['location'] = eval(x['location'])[
                                                            'ULocation']
            if driver_list_result[i].has_key('rack') and driver_list_result[i].has_key('location'):
                driver_list_result[i]['location_summary'] = driver_list_result[
                    i]['rack'] + ' : ' + driver_list_result[i]['location']
            else:
                driver_list_result[i]['location_summary'] = ''

    except:
        import traceback
        traceback.print_exc()
        driver_list_result = [
            {'name': u'drawer001', 'id': '1', 'description': 'test001',
             'model': '8721', 'location': '32U', 'status': 'normal',
             'uuid': '1726g21fg21y2t710', 'rack': 'rack001'},
            {'name': u'drawer002', 'id': '2', 'description': 'test002',
             'model': '8721', 'location': '1U', 'status': 'normal',
             'uuid': '1726g21fg21y1th12', 'rack': 'rack001'},
            {'name': u'drawer003', 'id': '10', 'description': 'test003',
             'model': '8721', 'location': '20U', 'status': 'normal',
             'uuid': '17d6g21fg21y1th13', 'rack': 'rack003'},
            {'name': u'drawer004', 'id': '4', 'description': 'test004',
             'model': '8721', 'location': '19U', 'status': 'normal',
             'uuid': '1726g11fg21y1th12', 'rack': 'rack003'},
            {'name': u'drawer005', 'id': '5', 'description': 'test005',
             'model': '8721', 'location': '11U', 'status': 'normal',
             'uuid': '1726g010g01y1th12', 'rack': 'rack006'}, ]
    for data in driver_list_result:
        rack_manager = RackManager(data)
        rack_managers_list.append(rack_manager)
    return rack_managers_list

@memoized
def pod_managers_list(request, refresh=False, project=''):
    kwargs = {}
    drawers_list = []
    try:
        if refresh == False:
            driver_vendor_result = driver_vendor_call(
                'pod_manager', 'get_pod_manager_list', **kwargs)
        else:
            pod_id = str(request.session['SELECTED_POD_MANAGER_ID'])
            kwargs = {'pod_id': pod_id}
            try:
                driver_vendor_result = driver_vendor_call(
                    'pod_manager', 'inventory_pod_manager_resources', **kwargs)
            except:
                pass
            while True:
                status_result = driver_vendor_call(
                    'pod_manager', 'get_pod_inventory_status', **kwargs)
                if extract_driver_dict_result(status_result) == 'finished':
                    break
                else:
                    import time
                    time.sleep(10)
            driver_vendor_result = driver_vendor_call(
                'pod_manager', 'get_pod_manager_list', **kwargs)

        driver_list_result = extract_driver_dict_result(driver_vendor_result)
    except:
        import traceback
        traceback.print_exc()
        driver_list_result = [
            {'name': u'PM001', 'id': '1', 'description': 'test001',
             'username': 'David', 'password': '123456', 'ip': '10.12.21.221',
             'status': 'normal', 'link': 'http://haha.com'},
            {'name': u'PM002', 'id': '2', 'description': 'test002',
             'username': 'Alice', 'password': '123456', 'ip': '10.12.21.21',
             'status': 'normal', 'link': 'http://haha.com'},
            {'name': u'PM003', 'id': '3', 'description': 'test003',
             'username': 'Bob', 'password': '123456', 'ip': '10.12.21.231',
             'status': 'normal', 'link': 'http://haha.com'},
            {'name': u'PM004', 'id': '4', 'description': 'test004',
             'username': 'Andy', 'password': '123456', 'ip': '10.12.21.224',
             'status': 'normal', 'link': 'http://haha.com'},
            {'name': u'PM005', 'id': '5', 'description': 'test005',
             'username': 'Tom', 'password': '123456', 'ip': '10.12.21.222',
             'status': 'normal', 'link': 'http://haha.com'}, ]
    for data in driver_list_result:
        drawer = Drawer(data)
        drawers_list.append(drawer)

    return drawers_list

@memoized
def manage_pod_manager(request, project='', **meta):
    kwargs = meta
    try:
        driver_vendor_result = driver_vendor_call(
            'pod_manager', 'manage_pod_manager', **kwargs)
        return driver_vendor_result
    except:
        import traceback
        traceback.print_exc()

@memoized
def unmanage_pod_manager(request, pod_id, project=''):
    kwargs = {
                'pod_manager_id': pod_id,
            }
    try:
        driver_vendor_result = driver_vendor_call(
            'pod_manager', 'unmanage_pod_manager', **kwargs)
        return driver_vendor_result
    except:
        import traceback
        traceback.print_exc()

@memoized
def composed_servers_list(request, pod_id, refresh=False, project=''):
    kwargs = {
                #'refresh': str(refresh),
                #'project':project,
                'pod_id': pod_id,
                #'node_type': 'Logical'
            }
    composed_servers_list = []
    try:
        if refresh == False:
            driver_vendor_result = driver_vendor_call(
                'pod_manager', 'get_composed_node_list', **kwargs)
        else:
            driver_vendor_result = driver_vendor_call(
                'pod_manager', 'inventory_composed_node', **kwargs)
        driver_list_result = extract_driver_dict_result(driver_vendor_result)
        for i, x in enumerate(driver_list_result):
            driver_list_result[i]['composedstate'] = 'Allocated'
            driver_list_result[i]['status_2'] = eval(x['status'])['Health']
            if x['location'] != '' and 'Rack' in eval(x['location']):
                driver_list_result[i]['rack_2'] = eval(x['location'])['Rack']
            if x['location'] != '' and 'ULocation' in eval(x['location']):
                driver_list_result[i]['u_location'] = eval(x['location'])[
                                                           'ULocation']
            try:
                driver_list_result[i]['location_summary'] = str(driver_list_result[
                    i]['rack_2']) + ' : ' + str(driver_list_result[i]['u_location'])
            except:
                import traceback
                traceback.print_exc()
                pass
            # driver_list_result[i]['name'] = 'Composed Node-' + str(i+1)
            if len(driver_list_result[i]['description']) >= 40:
                driver_list_result[i]['description'] = driver_list_result[i][
                    'description'][
                    : 40] + '...'
            #driver_list_result[i]['rack'] = eval(x['location'])['Rack']
    except:
        import traceback
        traceback.print_exc()
        driver_list_result = [
            {'name': u'server001', 'id': '1', 'description': 'test001',
             'power': 'on', 'composedstate': 'finished', 'model': 'x220',
             'assettag': 'active', 'rack': 'rack001', 'location': '1U',
             'status': 'normal'},
            {'name': u'server002', 'id': '2', 'description': 'test002',
             'power': 'off', 'composedstate': 'finished', 'model': 'x220',
             'assettag': 'active', 'rack': 'rack001', 'location': '2U',
             'status': 'normal'},
            {'name': u'server003', 'id': '3', 'description': 'test003',
             'power': 'off', 'composedstate': 'finished', 'model': 'x220',
             'assettag': 'active', 'rack': 'rack003', 'location': '1U',
             'status': 'normal'},
            {'name': u'server004', 'id': '4', 'description': 'test004',
             'power': 'off', 'composedstate': 'finished', 'model': 'x220',
             'assettag': 'active', 'rack': 'rack001', 'location': '3U',
             'status': 'normal'},
            {'name': u'server005', 'id': '5', 'description': 'test005',
             'power': 'on', 'composedstate': 'finished', 'model': 'x220',
             'assettag': 'active', 'rack': 'rack001', 'location': '4U',
             'status': 'normal'}, ]
    for data in driver_list_result:
        servers = ComposedServer(data)
        composed_servers_list.append(servers)

    return composed_servers_list

@memoized
def get_ethernet_switch_by_id(request, switch_id, refresh=False, project=''):
    kwargs = {
                'project': project,
                'switch_id': switch_id,
            }
    switch = {}
    driver_vendor_result = driver_vendor_call(
        'pod_manager', 'get_switch_info', **kwargs)
    origin_result = re.findall(r"<Driver (.+)>", driver_vendor_result.__str__())
    if origin_result:
        result = eval(origin_result[0])
    switch = result
    return switch

def get_composed_server_or_computer_system_by_id(
        request, pod_id, server_id, refresh=False, project=''):
    kwargs = {
                'pod_id': pod_id,
                'node_id': server_id,
            }
    composed_server = {}
    driver_vendor_result = driver_vendor_call(
        'pod_manager', 'get_composed_node_info', **kwargs)
    origin_result = re.findall(r"<Driver (.+)>", driver_vendor_result.__str__())
    if origin_result:
        result = eval(origin_result[0])
    composed_server = result
    return composed_server

def get_computer_system_by_id(
        request, pod_id, server_id, refresh=False, project=''):
    kwargs = {
                'pod_id': pod_id,
                'system_id': server_id,
            }
    composed_server = {}
    driver_vendor_result = driver_vendor_call(
        'pod_manager', 'get_computer_system_info', **kwargs)
    origin_result = re.findall(r"<Driver (.+)>", driver_vendor_result.__str__())
    if origin_result:
        result = eval(origin_result[0])
    composed_server = result
    return composed_server

def get_rack_server_offset(pod_id):
    kwargs = {
                'pod_id': str(pod_id),
             }
    driver_vendor_result = driver_vendor_call(
        'pod_manager', 'get_node_base_id', **kwargs)
    origin_result = re.findall(r"<Driver (.+)>", driver_vendor_result.__str__())
    if origin_result:
        result = eval(origin_result[0])
    return result['data']


def get_rack_info(chassis_id):
    kwargs = {
                'chassis_id': str(chassis_id),
             }
    driver_vendor_result = driver_vendor_call(
        'pod_manager', 'get_rack_info', **kwargs)
    origin_result = re.findall(r"<Driver (.+)>", driver_vendor_result.__str__())
    if origin_result:
        result = eval(origin_result[0])
    return result['data']

def get_rack_hardware_summary(request, pod_id, rack_id):
    kwargs = {'pod_id': pod_id, 'rack_id': rack_id}
    driver_vendor_result = driver_vendor_call(
        'pod_manager', 'get_rack_hardware_summary', **kwargs)
    origin_result = re.findall(r"<Driver (.+)>", driver_vendor_result.__str__())
    if origin_result:
        result = eval(origin_result[0])
    return result['data']

def get_resource_summary(pod_id):
    kwargs = {'pod_id': pod_id}
    driver_vendor_result = driver_vendor_call(
        'pod_manager', 'get_resource_summary', **kwargs)
    origin_result = re.findall(r"<Driver (.+)>", driver_vendor_result.__str__())
    if origin_result:
        result = eval(origin_result[0])
    return result['data']

def get_pod_manager_hardware_summary(request, pod_id):
    kwargs = {'pod_id': pod_id}
    driver_vendor_result = driver_vendor_call(
        'pod_manager', 'get_pod_manager_hardware_summary', **kwargs)
    origin_result = re.findall(r"<Driver (.+)>", driver_vendor_result.__str__())
    if origin_result:
        result = eval(origin_result[0])
    return result['data']

def get_rack_server_by_id(
    request,
    pod_id,
    server_id,
    refresh=False,
     project=''):
    '''
    kwargs_for_list = {
                'pod_id': pod_id,
            }
    driver_vendor_result_for_list = driver_vendor_call(
        'pod_manager', 'get_computer_system_list', **kwargs_for_list)
    origin_result_for_list = re.findall(r"<Driver (.+)>", driver_vendor_result_for_list.__str__())
    id_list = [item['id'] for item in eval(origin_result_for_list[0])['data']]
    composed_server = {}
    #offset = get_rack_server_offset(pod_id)
    offset = id_list[0] - 1
    kwargs = {
                # 'node_id': int(server_id) + offset,
                'system_id': int(server_id) + offset ,
            }
    if int(server_id) == 30:
        kwargs = {
                    'chassis_id': int(server_id) ,
                }
        driver_vendor_result = driver_vendor_call(
            'pod_manager', 'get_chassis_info', **kwargs)
        origin_result = re.findall(r"<Driver (.+)>", driver_vendor_result.__str__())
        if origin_result:
            result = eval(origin_result[0])
        composed_server = result
        return composed_server
    '''
    try:
        kwargs = {
                    'pod_id': int(pod_id) ,
                    'system_id': int(server_id) ,
                }
        if int(server_id) == 9999:
            driver_vendor_result = driver_vendor_call(
                'pod_manager', 'get_pcie_switch', **kwargs)
        else:
            driver_vendor_result = driver_vendor_call(
                'pod_manager', 'get_computer_system_info', **kwargs)
    except:
        kwargs = {
                    'switch_id': int(server_id) ,
                }
        driver_vendor_result = driver_vendor_call(
            'pod_manager', 'get_switch_info', **kwargs)
    origin_result = re.findall(r"<Driver (.+)>", driver_vendor_result.__str__())
    if origin_result:
        result = eval(origin_result[0])
    composed_server = result
    return composed_server


def get_drawer_by_id(request, pod_id, chassis_id, refresh=False, project=''):
    kwargs = {
                'pod_id': pod_id,
                'chassis_id': chassis_id,
            }
    drawer = {}
    driver_vendor_result = driver_vendor_call(
        'pod_manager', 'get_drawer_info', **kwargs)
    origin_result = re.findall(r"<Driver (.+)>", driver_vendor_result.__str__())
    if origin_result:
        result = eval(origin_result[0])
    drawer = result
    return drawer

def test(request):
    kwargs = {}
    driver_vendor_result = driver_vendor_call(
        'pod_manager', 'get_drawer_info', **kwargs)
    origin_result = re.findall(r"<Driver (.+)>", driver_vendor_result.__str__())
    if origin_result:
        result = eval(origin_result[0])
    drawer = result
    return drawer


def get_rack_manager_by_id(request, manager_id, refresh=False, project=''):
    kwargs = {
                'manager_id': manager_id,
            }
    rack_manager = {}
    driver_vendor_result = driver_vendor_call(
        'pod_manager', 'get_rack_manager_info', **kwargs)
    origin_result = re.findall(r"<Driver (.+)>", driver_vendor_result.__str__())
    if origin_result:
        result = eval(origin_result[0])
    rack_manager = result
    return rack_manager

@memoized
def virtualdisks_list(request, pod_id, refresh=False, project=''):
    kwargs = {
            #'refresh': str(refresh),
            'project': project,
            'pod_id': pod_id
            }
    virtualdisks_list = []
    try:
        if refresh == False:
            driver_vendor_result = driver_vendor_call(
                'pod_manager', 'get_volume_list', **kwargs)
        else:
            driver_vendor_result = driver_vendor_call(
                'pod_manager', 'inventory_volumes', **kwargs)
        driver_list_result = extract_driver_dict_result(driver_vendor_result)
        for i, x in enumerate(driver_list_result):
            driver_list_result[i]['capacity'] = x['size_GB']
            driver_list_result[i]['status_2'] = 'OK'
            driver_list_result[i]['rack_2'] = 'Rack1'
            #driver_list_result[i]['status_2'] = eval(x['status'])['Health']
            #if 'Rack' in eval(x['location']):
            #    driver_list_result[i]['rack_2'] = eval(x['location'])['Rack']
    except:
        import traceback
        traceback.print_exc()
        driver_list_result = [
            {'name': u'VD001', 'id': '1', 'description': 'test001',
             'status': 'normal', 'health': 'normal', 'type': 'x500',
             'mode': 'active', 'capacity': '100T', 'image': 'notknown',
             'bootable': 'yes', 'rack': 'rack006'},
            {'name': u'VD002', 'id': '2', 'description': 'test002',
             'status': 'normal', 'health': 'normal', 'type': 'x500',
             'mode': 'active', 'capacity': '100T', 'image': 'notknown',
             'bootable': 'yes', 'rack': 'rack001'},
            {'name': u'VD003', 'id': '3', 'description': 'test003',
             'status': 'normal', 'health': 'normal', 'type': 'x500',
             'mode': 'active', 'capacity': '100T', 'image': 'notknown',
             'bootable': 'yes', 'rack': 'rack001'},
            {'name': u'VD004', 'id': '4', 'description': 'test004',
             'status': 'normal', 'health': 'normal', 'type': 'x500',
             'mode': 'active', 'capacity': '100T', 'image': 'notknown',
             'bootable': 'yes', 'rack': 'rack006'},
            {'name': u'VD005', 'id': '5', 'description': 'test005',
             'status': 'normal', 'health': 'normal', 'type': 'x500',
             'mode': 'active', 'capacity': '100T', 'image': 'notknown',
             'bootable': 'yes', 'rack': 'rack006'}, ]
    for data in driver_list_result:
        vds = VirtualDisk(data)
        virtualdisks_list.append(vds)

    return virtualdisks_list

@memoized
def storage_list(request, pod_id, refresh=False, project=''):
    kwargs = {
            'project': project,
            'pod_id': pod_id
            }
    try:
        driver_vendor_result = driver_vendor_call(
            'pod_manager', 'get_storage_list', **kwargs)
        driver_list_result = extract_driver_dict_result(driver_vendor_result)
        storage_list = driver_list_result['storage_list']
        storage_table_name = driver_list_result['storage_name']
    except:
        import traceback
        traceback.print_exc()

    return storage_table_name, storage_list


def get_virtual_disk_by_id(request, pod_id, volume_id, refresh=False, project=''):
    kwargs = {
                'pod_id': pod_id,
                'volume_id': volume_id,
            }
    virtual_disk = {}
    driver_vendor_result = driver_vendor_call(
        'pod_manager', 'get_volume_info', **kwargs)
    origin_result = re.findall(r"<Driver (.+)>", driver_vendor_result.__str__())
    if origin_result:
        result = eval(origin_result[0])
    virtual_disk = result
    return virtual_disk

def get_rack_view(request, pod_id, rack_id, refresh=False, project=''):
    kwargs = {
                'pod_id': pod_id,
                'rack_id': rack_id,
            }
    rack_css_class_list = []
    rack_location_index = []
    driver_vendor_result = driver_vendor_call(
        'pod_manager', 'get_rack_view', **kwargs)
    origin_result = re.findall(r"<Driver (.+)>", driver_vendor_result.__str__())
    if origin_result:
        result = eval(origin_result[0])
    components = result['data']
    ulocation_pointer = 0
    for c in components:
        if 'ULocation' in c.keys():
            ulocation = int(filter(str.isdigit, str(c['ULocation'])))
            uheight = int(filter(str.isdigit, str(c['UHeight'])))
            ulocation = 42 - ulocation - uheight
            location_offset = ulocation-ulocation_pointer
            for i in xrange(0, location_offset):
                rack_css_class_list.append('blank_1u')
                rack_location_index.append(0)
                ulocation_pointer += 1
                if ulocation_pointer==23:
                    rack_css_class_list.pop()
                    rack_css_class_list.pop()
                    rack_location_index.pop()
                    rack_location_index.pop()
                    rack_css_class_list.append('pcie_switch_2u')
                    rack_location_index.append('9999')

        if 'name' in c.keys() and 'switch' in c['name'] :
            rack_css_class_list.append('switch_1u')
            rack_location_index.append(c['id'])
            ulocation_pointer += 1
        else:
            if len(c['computer_systems']) > 1 :
                append_rack_css_class_list = ['blank_half_width_1u' for x in range(0, 14)]
                append_rack_location_index = [0 for x in range(0, 14)]
                index_rebuilt = [12, 13, 10, 11, 8, 9, 6, 7, 4, 5, 2, 3, 0, 1]
                rack_css_class_list.append('chassis_begin')
                rack_location_index.append(0)
                for i, cs in enumerate(c['computer_systems']):
                    append_rack_css_class_list[index_rebuilt[cs['system_location']-1]] = 'rack_half_width_1u'
                    append_rack_location_index[index_rebuilt[cs['system_location']-1]] = cs['system_id']
                    # rack_css_class_list.append('rack_half_width_1u')
                    # rack_location_index.append(i['system_id'])
                rack_css_class_list += append_rack_css_class_list
                rack_location_index += append_rack_location_index
                rack_css_class_list.append('chassis_end')
                rack_location_index.append(0)
                ulocation_pointer += int(filter(str.isdigit, str(c['UHeight']))) + 1
            if len(c['computer_systems']) == 1 :
                if int(filter(str.isdigit, str(c['UHeight']))) == 1:
                    rack_css_class_list.append('rack_1u')
                    rack_location_index.append(c['computer_systems'][0]['system_id'])
                    ulocation_pointer += 1
                elif int(filter(str.isdigit, str(c['UHeight']))) == 2:
                    rack_css_class_list.append('storage_2u')
                    rack_location_index.append(c['computer_systems'][0]['system_id'])
                    ulocation_pointer += 2
    for i in xrange(0, 42-ulocation_pointer):
        rack_css_class_list.append('blank_1u')
        rack_location_index.append(0)

    return rack_css_class_list, rack_location_index

@memoized
def racks_list(request, pod_id, refresh=False, project=''):
    kwargs = {
                #'refresh': str(refresh),
                #'project':project,
                'pod_id': pod_id,
                'chassis_type': 'Rack'
            }
    racks_list = []
    try:
        if refresh == False:
            driver_vendor_result = driver_vendor_call(
                'pod_manager', 'get_rack_list', **kwargs)
        else:
            driver_vendor_result = driver_vendor_call(
                'pod_manager', 'inventory_rsa_chassis', **kwargs)
        driver_list_result = extract_driver_dict_result(driver_vendor_result)
        for i, x in enumerate(driver_list_result):
            driver_list_result[i]['status_2'] = eval(x['status'])['Health']
    except:
        import traceback
        traceback.print_exc()
        driver_list_result = [{'name': u'Rack001', 'id': '1',
                               'description': 'test001', 'status': 'normal',
                               'health': 'good', 'type': 'x500', 'mode': '8721',
                               'capacity': '100T', 'image': 'notknown',
                               'bootable': 'yes',
                               'serialnumber': 'Mdx02398329'},
                              {'name': u'RackD002', 'id': '2',
                               'description': 'test002', 'status': 'normal',
                               'health': 'good', 'type': 'x500', 'mode': '8721',
                               'capacity': '100T', 'image': 'notknown',
                               'bootable': 'yes',
                               'serialnumber': 'Mdx02398822'},
                              {'name': u'Rack003', 'id': '3',
                               'description': 'test003', 'status': 'normal',
                               'health': 'good', 'type': 'x500', 'mode': '8721',
                               'capacity': '100T', 'image': 'notknown',
                               'bootable': 'yes',
                               'serialnumber': 'Mdx02392222'},
                              {'name': u'RackD004', 'id': '4',
                               'description': 'test004', 'status': 'normal',
                               'health': 'good', 'type': 'x500', 'mode': '8721',
                               'capacity': '100T', 'image': 'notknown',
                               'bootable': 'yes',
                               'serialnumber': 'Mdx02333322'},
                              {'name': u'RackD005', 'id': '5',
                               'description': 'test005', 'status': 'normal',
                               'health': 'good', 'type': 'x500', 'mode': '8721',
                               'capacity': '100T', 'image': 'notknown',
                               'bootable': 'yes',
                               'serialnumber': 'Mdx02393322'},
                              {'name': u'Rack006', 'id': '6',
                               'description': 'test005', 'status': 'normal',
                               'health': 'good', 'type': 'x500', 'mode': '8721',
                               'capacity': '100T', 'image': 'notknown',
                               'bootable': 'yes',
                               'serialnumber': 'Mdx02390001'}, ]
    for data in driver_list_result:
        rack = Rack(data)
        racks_list.append(rack)

    return racks_list


@memoized
def blades_list(request, pod_id, refresh=False, project=''):
    kwargs = {
                #'refresh': str(refresh),
                #'project':project,
                'pod_id': pod_id,
                #'node_type': 'Physical'
            }
    blades_list = []
    try:
        if not refresh:
            driver_vendor_result = driver_vendor_call(
                'pod_manager', 'get_computer_system_list', **kwargs)
        else:
            driver_vendor_result = driver_vendor_call(
                'pod_manager', 'inventory_computer_system', **kwargs)
        driver_list_result = extract_driver_dict_result(driver_vendor_result)
        for i, x in enumerate(driver_list_result):
            driver_list_result[i]['status_2'] = eval(x['status'])['Health']
            try:
                if 'Rack' in eval(x['location']):
                    driver_list_result[i]['rack_2'] = eval(x['location'])['Rack']
                if 'ULocation' in eval(x['location']):
                    driver_list_result[i]['u_location'] = eval(x['location'])[
                                                            'ULocation']
                driver_list_result[i]['location_summary'] = str(driver_list_result[
                    i]['rack_2']) + ' : ' + str(driver_list_result[i]['u_location'])
                if len(driver_list_result[i]['description']) >= 40:
                    driver_list_result[i]['description'] = driver_list_result[i][
                        'description'][
                        : 40] + '...'
            except:
                pass
    except:
        import traceback
        traceback.print_exc()
        driver_list_result = [
            {'name': u'Compute system 001', 'id': '1', 'description': 'test001',
             'health': 'normal', 'hostname': 'x500', 'model': 'sx200',
             'rack': 'rack003', 'location': '2U'},
            {'name': u'Compute system 002', 'id': '2', 'description': 'test002',
             'health': 'normal', 'hostname': 'x500', 'model': 'sx200',
             'rack': 'rack001', 'location': '3U'},
            {'name': u'Compute system 003', 'id': '3', 'description': 'test003',
             'health': 'normal', 'hostname': 'x500', 'model': 'sx200',
             'rack': 'rack001', 'location': '5U'},
            {'name': u'Compute system 004', 'id': '4', 'description': 'test004',
             'health': 'normal', 'hostname': 'x500', 'model': 'sx200',
             'rack': 'rack001', 'location': '8U'},
            {'name': u'Compute system 005', 'id': '5', 'description': 'test005',
             'health': 'normal', 'hostname': 'x500', 'model': 'sx200',
             'rack': 'rack003', 'location': '6U'}, ]
    for data in driver_list_result:
        blade = Blade(data)
        blades_list.append(blade)

    return blades_list

@memoized
def events_list(request, refresh=False, project=''):
    events_list = []
    driver_list_result = [
        {'time': u'2016-2-23', 'id': '1', 'message': 'test001',
         'eventtype': 'routine', 'target': 'x500'},
        {'time': u'2016-2-23', 'id': '2', 'message': 'test002',
         'eventtype': 'routine', 'target': 'x500'},
        {'time': u'2016-2-23', 'id': '3', 'message': 'test003',
         'eventtype': 'routine', 'target': 'x500'},
        {'time': u'2016-2-23', 'id': '4', 'message': 'test004',
         'eventtype': 'routine', 'target': 'x500'},
        {'time': u'2016-2-23', 'id': '5', 'message': 'test005',
         'eventtype': 'routine', 'target': 'x500'}, ]
    for data in driver_list_result:
        event = Event(data)
        events_list.append(event)

    return events_list
