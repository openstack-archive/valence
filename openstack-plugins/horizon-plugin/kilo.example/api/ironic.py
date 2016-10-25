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
from openstack_dashboard.api import confluent
from django.utils.translation import ugettext_lazy as _
from oslo.utils import importutils
from horizon import exceptions
from horizon.utils.memoized import memoized  # noqa
from django.conf import settings
import re
import time
import logging
import datetime
from openstack_dashboard.api import nova
LOG = logging.getLogger(__name__)


ironic_cli = None


class IronicClientWrapper(object):
    """Ironic client wrapper class that encapsulates retry logic."""

    def __init__(self):
        """Initialise the IronicClientWrapper for use.
        Initialise IronicClientWrapper by loading ironicclient.
        """
        global ironic_cli
        if ironic_cli is None:
            ironic_cli = importutils.import_module('ironicclient')
            if not hasattr(ironic_cli, 'exc'):
                ironic_cli.exc = importutils.import_module('ironicclient.exc')
            if not hasattr(ironic_cli, 'client'):
                ironic_cli.client = importutils.import_module(
                                                    'ironicclient.client')
        self.ironiclient_config = getattr(settings, 'IRONIC_ADMIN_USER', {})
        
    def _get_ironic_client(self):
        """return an Ironic client."""
        #get the data from django setting files        
        kwargs = {'os_username': self.ironiclient_config.get('username', ''),
                  'os_password': self.ironiclient_config.get('password', ''),
                  'os_auth_url': self.ironiclient_config.get('auth_url', ''),
                  'os_tenant_name': self.ironiclient_config.get('tenant_name', ''),
                  'os_service_type': self.ironiclient_config.get('service_type', ''),
                  'os_endpoint_type': self.ironiclient_config.get('endpoint_type', ''),
                  'ironic_url': self.ironiclient_config.get('ironic_url', '')}
        try:
            cli = ironic_cli.client.get_client(1, **kwargs)
        except ironic_cli.exc.Unauthorized:
            msg = _("Unable to authenticate Ironic client.")            
            LOG.warn(msg)
            
        return cli

    def _multi_getattr(self, obj, attr):
        """Support nested attribute path for getattr().
        """        
        for attribute in attr.split("."):
            obj = getattr(obj, attribute)
        return obj

    def callmethod(self, callmethod, *callargs, **callkwargs):
        """Call an Ironic client method and retry on errors.
        :param method: Name of the client method to call as a string.
        :param args: Client method arguments.
        :param kwargs: Client method keyword arguments.
        """
        retry_excs = (ironic_cli.exc.ServiceUnavailable,
                      ironic_cli.exc.ConnectionRefused,
                      ironic_cli.exc.Conflict)
        num_attempts = 60
        for attempt in range(1, num_attempts + 1):
            client = self._get_ironic_client()
            try:
                exe_method=self._multi_getattr(client, callmethod)   
                if callargs:
                    return exe_method(*callargs, **callkwargs)
                else:              
                    return exe_method(**callkwargs)
            except retry_excs:
                msg = (_("Error contacting Ironic server for '%(method)s'. "
                         "Attempt %(attempt)d of %(total)d")
                       % {'method': callmethod,
                          'attempt': attempt,
                          'total': num_attempts})
                if attempt == num_attempts:
                    LOG.error(msg)
                LOG.warning(msg)
                time.sleep(self.ironiclient_config.getattr(settings, 'retry_interval', 2))

client=IronicClientWrapper()
    
"""
=================================================================================================
"""   
 
class PhysicalServer(base.APIDictWrapper):
    """physical server in dict, for xClarity driver, we put the detail info in extra field"""


    _attrs = ['name', 'vendor_name', 'uuid', 'power_state', 'product_name', 'management_ip', 'cpu', 'memory', 'disk', 'nic', 
              'location', 'physical_uuid', 'hasOS', 'assigned', 'applied', 'project', 'provision_state', 'readyCheck', 
              'mac_addresses', 'console_user', 'console_passwd', 'firmware','fodkey', 'access_state','hypervisor', 'hypervisor_type']
            
    @property
    def name(self):
        return self._apidict['extra'].get('name','')
    
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
    
"""
=================================================================================================
""" 
    
class RequestCandidate(base.APIDictWrapper):
    """Approval list in dict, we may need to add [project, user, request_at, action_at, ] etc.
    and make the project user can see the request status"""
    #here _attrs only means we can know the properties
    _attrs = ['tenant_id', 'tenant_name', 'flavor_id', 'flavor_name', 'number', 'rule', 'id','created_at', 'updated_at']
     
    @property
    def status(self):
        return 'wait for approve'
    @property
    def wait_time(self):
        str_time = self._apidict['created_at']
        created_at = None
        for fmt in ["%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S.%f",
                    "%Y-%m-%d %H:%M:%S.%f"
                    "%Y-%m-%d %H:%M:%S"]:
            try:
                created_at = datetime.datetime.strptime(str_time,fmt)
                break
            except Exception as e:
                pass
        if created_at:
            current_time  = datetime.datetime.now()
            return (current_time - created_at)
        else:
            return 'unknown'
        
"""
=================================================================================================
""" 
class XClarityInstance(base.APIDictWrapper):
    """xClarity(xhmc) in a dict, we may need to add server individually(heterogeneous servers)"""
    
    _attrs = ['id','ipaddress', 'username', 'password', 'link', 'state',]
               
"""
=====================================================================
"""       

def extract_driver_list_result(driver_result):
    """the driver vendor method return list result, parse the result to get it"""
    datalist=[]
    orig_driver_data= re.findall(r"<Driver (.+)>", driver_result.__str__())
    if orig_driver_data:
        datalist = eval(orig_driver_data[0])['data']
    return datalist

def extract_driver_dict_result(driver_result):
    result={}
    origin_result= re.findall(r"<Driver (.+)>", driver_result.__str__())
    if origin_result:
        result=eval(origin_result[0])['data']
    return result

def extract_node_dict_result(node_result):
    """the node vendor method return string result"""
    orig_node_data= re.findall(r"<Node (.+)>", node_result.__str__())
    if orig_node_data:        
        return eval(orig_node_data[0])['data']
    return None

"""
=====================================================================
"""
#mainly driver call, driver vendor call, node call, node vendor call

def driver_vendor_call(driver_name, method_name, **kwargs):
    #check driver_name, method_name
    if driver_name is None or driver_name == "" or method_name is None or method_name == "":
        return None
    
    #driver vendor method
    kwargs = {
        'driver_name' : driver_name,
        'method' : method_name,    
        'args' : kwargs,    
        }
    
    method = "driver.vendor_passthru"
    vendor_call_result = client.callmethod(method, **kwargs)
    #check or not?
    return vendor_call_result

def node_vendor_call(node_uuid, method_name, **kwargs):
    if node_uuid is None or node_uuid == "" or method_name is None or method_name == "":
        return None
    
    kwargs={
        'method' : method_name,
        'node_id' : node_uuid,
        'args' : kwargs              
        }
        
    method="node.vendor_passthru" 
    client.callmethod(method, **kwargs)
    
def node_method_call(node_uuid, method_name, action):
    #node method may not only set provision
    method="node."+method_name
    client.callmethod(method, node_uuid, action)
         
"""
=====================================================================
"""

@memoized
def physical_server_list(request, refresh=False, project=''):
    """Get the list of available xclarity physical server.
    and get the list of available ipmi server(maybe more)"""
    kwargs={
                'refresh':str(refresh),
                'project':project
            }
    
    driver_vendor_result = driver_vendor_call('lenovo_xclarity', 'inventory', **kwargs)
        
    server_list=[]
    for data in extract_driver_list_result(driver_vendor_result):
        """we iterator the node list, and format the PhysicalServer in dict""" 
        phy = PhysicalServer(data)
        server_list.append(phy);

    return server_list

def physical_server_get(request, server_id):
    """Get the physical server detail."""
    
    kwargs={'node_id':server_id,}    
    driver_vendor_result = driver_vendor_call('lenovo_xclarity', 'get_node_by_uuid', **kwargs)    
    server_dict = extract_driver_dict_result(driver_vendor_result)
    if server_dict:
        return PhysicalServer(server_dict)
    return None

def add_ipmi_physical_server(request, **meta):
    
    kwargs={}
    kwargs['driver'] = 'pxe_ipminative'
    driver_info={}
    driver_info['ipmi_address'] = meta.get('ipmi_ip','')
    driver_info['ipmi_username'] = meta.get('ipmi_user','')
    driver_info['ipmi_password'] = meta.get('ipmi_pass','')
    driver_info['ipmi_terminal_port'] = meta.get('ipmi_port','')    
    kwargs['driver_info'] = driver_info
    
    extra={}
    extra['name'] = meta.get('server_name','')
    extra['vendor_name'] = meta.get('vendor_name','')
    extra['product_name'] = meta.get('model','')
    extra['cpu'] = meta.get('cpu_number','')
    extra['memory'] = meta.get('memory_size','')
    extra['disk'] = meta.get('disk_size','')    
    kwargs['extra'] = extra
      
    driver_vendor_call('lenovo_xclarity', 'add_physical_server', **kwargs)    
    
def associate_hypervisor (request, obj_id, hypervisor_id, hypervisor_name):
    kwargs={}
    kwargs['uuid'] = obj_id
    
    extra={}
    if hypervisor_id != '':
        extra['hypervisor'] = hypervisor_id   
        extra['hypervisor_name'] = hypervisor_name 
        # extra['hypervisor_type'] = hypervisor_type 
    else:
        extra['hypervisor'] = ''   
        extra['hypervisor_name'] = ''         
    kwargs['extra'] = extra
    
    driver_vendor_call('lenovo_xclarity', 'edit_physical_server', **kwargs) 
            
def edit_ipmi_physical_server(request, obj_id, **meta):
    
    kwargs={}
    kwargs['uuid'] = obj_id
    kwargs['driver'] = 'pxe_ipminative'
    driver_info={}
    driver_info['ipmi_address'] = meta.get('ip_address','')
    driver_info['ipmi_username'] = meta.get('ipmi_user','')
    driver_info['ipmi_password'] = meta.get('ipmi_pass','')
    driver_info['ipmi_terminal_port'] = meta.get('ipmi_port','')    
    kwargs['driver_info'] = driver_info
    
    extra={}
    extra['name'] = meta.get('server_name','')
    extra['vendor_name'] = meta.get('vendor_name','')
    extra['product_name'] = meta.get('model','')
    extra['cpu'] = meta.get('cpu_number','')
    extra['memory'] = meta.get('memory_size','')
    extra['disk'] = meta.get('disk_size','')    
    kwargs['extra'] = extra
    
    driver_vendor_call('lenovo_xclarity', 'edit_physical_server', **kwargs) 
    

def physical_servers_stats(request):
    #get the statics of the physical server
    
    kwargs={}
    driver_vendor_result = driver_vendor_call('lenovo_xclarity', 'physical_servers_stats', **kwargs)
    result_dict = extract_driver_dict_result(driver_vendor_result)
    return result_dict
        
def remove_physical_server(request, obj_id):
    #remove the physical server
       
    kwargs={'uuid':obj_id}
    driver_vendor_call('lenovo_xclarity', 'remove_physical_server', **kwargs)

def resource_pool_usage(request):
    """Get resource pool."""
    
    kwargs={}
    driver_vendor_result = driver_vendor_call('lenovo_xclarity', 'get_resource_pool_usage', **kwargs)
    server_dict = extract_driver_dict_result(driver_vendor_result)
    return server_dict


def get_available_os_types(request, uuid):
    """call xClarity rest api to get the available os"""

    kwargs={'uuid':uuid}
    driver_vendor_result = driver_vendor_call('lenovo_xclarity', 'show_images', **kwargs)
    result=extract_driver_dict_result(driver_vendor_result)
    
    os_types=[]
    os_types.append(('',_('Select OS Type')))    
    #parse the result to 
    if result:
        items = result['items']
        for item in items:
            profiles = item['profiles']
            for profile in profiles:
                name=profile['id']
                show_name=profile['name']
                one_os=(name, show_name)
                os_types.append(one_os)

    return os_types

def deploy_os(request, obj_id, **meta):
    """call xClarity rest api to deploy os, we may need to do the global setting and other rest calls in horizon"""
    
    """step 1, prepare, which means, add the parameters"""
    args={
        'uuid': meta['physical_id'],    
        'selected_image': meta['select_os'],
        'storage_device': meta['disk_type'],
        'selected_mac': meta['select_mac'],
        'ip_address': meta['ip'],
        'subnet_mask': meta['subnetmask'],
        'gateway': meta['gateway'],
        'dns1': meta['dns1'],
        'dns2': meta['dns2'],       
        'mtu': meta['mtu'],  
        }     
    
    node_vendor_call(obj_id, "deploy_prepare", **args)
    
    #need to check the deploy_prepare correct or not? maybe we don't need
    """step 2, do deploy"""
    """it should be active or rebuild, compatible with Juno, ironic
    in deploy failed, can accept the active status"""
    
    current_server=physical_server_get(request, obj_id)
    action='active'
    if current_server and current_server.provision_state == 'active':
        action='rebuild'

    node_method_call(obj_id, "set_provision_state", action)  

def physical_server_power_action(request, obj_id, action=''):
    """physical server power on/off, rebooting
       do we need to use a timer to check if the power state is successfully finished?
    """
    
    if action in ['rebooting', 'power off', 'power on']:        
        node_method_call(obj_id, "set_power_state", action)


def change_server_category(request, obj_id, action=''):
    """change server category: apply, public, free, reserve"""
    #need to check if action allowed
    args = {}
    if action in ['apply_node_by_uuid', 'public_node_by_uuid','free_node_by_uuid','reserve_node_by_uuid']:  
        node_vendor_call(obj_id, action, **args)      
    
def assign_servers(request, **filter_items):
    """assign servers to selected tenant, this method should be complexity in a certain way"""
    #assign what kind of servers, args works like "filters"
    args={}
    args['assign_number'] = filter_items.get('assign_number', '0')
    args['fixed_servers'] = filter_items.get('fixed_servers', '[]')
    args['target_tenant'] = filter_items.get('target_tenant', '')
    args['target_tenant_name'] = filter_items.get('target_tenant_name','')
    args['flavor_id'] = filter_items.get('flavor_id', '')
    args['flavor_name'] = filter_items.get('flavor_name','')
    args['rules'] = filter_items.get('rules','')
    #by default, the admin assign servers to project user, oppositely,project subscribe servers 
    args['direction'] = filter_items.get('direction', 'admin')        
    
    flavor_id = filter_items.get('flavor_id', '')
    if flavor_id != '':
        #we may take more into account
        flavor_detail = nova.flavor_get(request, flavor_id, False)
        args['cpu'] = getattr(flavor_detail, 'vcpus', None)
        memory = int(getattr(flavor_detail, 'ram', None))
        args['memory'] = float(memory/1024.0)
    
    driver_vendor_result = driver_vendor_call('lenovo_xclarity', 'assign_servers', **args)        
    extracted_result = extract_driver_dict_result(driver_vendor_result)
    if extracted_result:
        if extracted_result.get('result') == 'success':
            return 'Assigned successfully'
        elif extracted_result.get('result') == 'admin failed':
            return 'Cannot do assign operation'
        elif extracted_result.get('result') == 'project failed':
            return 'approve subscribe failed'
    
def update_console_info(request, obj_id, key, value):
    """update confluent user/password"""
    #the key should be 
    #hardwaremanagementpassword
    #hardwaremanagementuser
    kwargs={
            'key':key,
            'value':value
            }
    node_vendor_call(obj_id, "update_console_info", **kwargs)
    
    
def associate_auth(request, **meta):
    """update confluent user/password"""
    obj_id = meta.get('uuid')
    user = meta.get('user')
    passwd = meta.get('passwd')
        
    kwargs={
            'uuid': obj_id,
            'user':user,
            'passwd':passwd
            }
    driver_vendor_call('lenovo_xclarity', 'associate_console_auth', **kwargs)

"""
=====================================================================
"""

def subscribe_server(request, **kargs):
    """users request admin for servers"""
    args = {}
    args['subscribe_number'] = kargs.get('subscribe_number', 0)
    args['flavor_id'] = kargs.get('flavor_id', '')
    args['flavor_name'] = kargs.get('flavor_name', '')
    args['rules'] = kargs.get('rules', '')
    args['target_tenant'] = kargs.get('target_tenant', '')
    args['target_tenant_name'] = kargs.get('target_tenant_name', '')
    
    driver_vendor_call('lenovo_xclarity', 'subscribe_server', **args)


def get_subscribe_list(request, project=''):
    """get the subscribe request list of the users"""

    kwargs = {'project':project}
    driver_vendor_result = driver_vendor_call('lenovo_xclarity', 'get_subscribe_list', **kwargs)
    subscribe_list = extract_driver_list_result(driver_vendor_result)
    approval_list=[]
    for subscription in subscribe_list:
        #sub_dict = eval(subscription)
        tmp={}
        tmp['number']=subscription.get('number')
        tmp['tenant_id']=subscription.get('tenant_id')
        tmp['tenant_name']=subscription.get('tenant_name')
        tmp['flavor_id']=subscription.get('flavor_id')
        tmp['flavor_name']=subscription.get('flavor_name')
        tmp['rule']=subscription.get('rule')
        tmp['id']=subscription.get('id')
        tmp['created_at']=subscription.get('created_at')
        approval_list.append(RequestCandidate(tmp))    
    return approval_list


def get_subscribe(request, subscribe_id):
    """get a specified subscribe request by id"""
    args={'id':subscribe_id }    
    
    driver_vendor_result = driver_vendor_call('lenovo_xclarity', 'get_subscribe', **args)
    dict_result = extract_driver_dict_result(driver_vendor_result)
    if dict_result:
        tmp={}
        tmp['number']=dict_result.get('number')
        tmp['tenant_id']=dict_result.get('tenant_id')
        tmp['tenant_name']=dict_result.get('tenant_name')
        tmp['flavor_id']=dict_result.get('flavor_id')
        tmp['flavor_name']=dict_result.get('flavor_name')
        tmp['rule']=dict_result.get('rule')
        tmp['id']=dict_result.get('id')
        tmp['created_at']=dict_result.get('created_at')
        return RequestCandidate(tmp)
    return None


def reject_subscribe_request(request, obj_id):
    """Admin side reject subscribe request"""
    args={'id':obj_id}    
    driver_vendor_call('lenovo_xclarity', 'reject_subscribe_request', **args)

def resend_subscribe_request(request, obj_id):
    """Admin side reject subscribe request"""
    args={'id':obj_id}       
    driver_vendor_call('lenovo_xclarity', 'resend_subscribe_request', **args)

"""
=====================================================================
"""

def get_xclairty_instance_list(request):
    """get the managed xClarity instances from DB"""    
   
    kwargs={}     
    driver_vendor_result = driver_vendor_call('lenovo_xclarity', 'get_xclarity_list', **kwargs)
    result_list = extract_driver_list_result(driver_vendor_result)
    xhmcs=[]    
    for xclarity_inst in result_list:
        tmp={}
        tmp['id'] = xclarity_inst.get('id')
        tmp['ipaddress'] = xclarity_inst.get('ipaddress')
        tmp['username'] = xclarity_inst.get('username')
        tmp['password'] = xclarity_inst.get('password')
        tmp['link'] = xclarity_inst.get('link')
        tmp['state'] = xclarity_inst.get('state')
        xhmcs.append(XClarityInstance(tmp))        
    return xhmcs
    
    
def get_xclarity(request, xclarity_id):
    """get the specified xClarity by id"""
       
    kwargs={'id':xclarity_id}
    driver_vendor_result = driver_vendor_call('lenovo_xclarity', 'get_xclarity', **kwargs)
    result_dict = extract_driver_dict_result(driver_vendor_result)
    return XClarityInstance(result_dict)

def manage_xclarity(request, ip, user, passwd):
    """manage xClarity, add the info into DB"""
    args={
      'ipaddress':ip,
      'username':user,
      'password':passwd,
      'link':'https://'+ip
      }
    
    driver_vendor_call('lenovo_xclarity', 'manage_xclarity_instance', **args)
      
def edit_xclarity(request, xclarity_id, ip, user, passwd):
    """manage xClarity, add the info into DB"""
    args={
      'xclarity_id':xclarity_id,
      'ipaddress':ip,
      'username':user,
      'password':passwd,
      'link':'https://'+ip
      }    
    driver_vendor_call('lenovo_xclarity', 'edit_xclarity_instance', **args)
    
def configure_xclarity(request, ip_way):
    """manage xClarity, add the info into DB"""
    args={
      'ip_way':ip_way,      
      }
      
    driver_vendor_call('lenovo_xclarity', 'config_xclarity', **args)  

def get_global_settings(request):
    """manage xClarity, add the info into DB"""        
    args={}
    driver_vendor_result = driver_vendor_call('lenovo_xclarity', 'get_global_settings', **args)      
    result_dict = extract_driver_dict_result(driver_vendor_result)
    if result_dict:
        return result_dict["globalSetting"]['ipAssignment']  
    else:
        LOG.warn('while getting global settings, empty result')
        return None
    
     
def unmanage_xclarity(request, xclarity_id):
    """unmanage xClarity, remove from DB"""
    args={
      'id':xclarity_id,
      }
    driver_vendor_call('lenovo_xclarity', 'unmanage_xclarity_instance', **args)      
    