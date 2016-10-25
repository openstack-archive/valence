"""
using this module to make a wrapper in horizon, since there are multi-drivers supported(
currently lxca and ipmi native), in this class we do some check or call the ironic client 
to make a decision
"""

from openstack_dashboard.dashboards.admin.physical_servers import constants

def check_if_edit_server_allowed(server):
    """
    the node of lenovo_xclarity driver cannot be edited 
    """
    if server and server.driver != constants.LXCA_DRIVER:
        return True
    return False

def check_if_free_server_allowed(server):
    """
    the node in free state can not be freed again 
    """
    if server and server.assigned != '-1':
        return False
    return True

def check_if_reserve_server_allowed(server):
    """
    the node in reserved state can not be reserved again
    """
    if server and server.assigned == '-1':
        return False
    return True

def check_if_remove_server_allowed(server):
    """
    the node in disconnected state can not be removed
    we need manageable, provide...
    this can be changed
    """
    if server.access_state == 'disconnected':
        return True        
    return False


def check_if_deploy_action_allowed(server):
    """"currently, we only support the xclarity driver deploy
    in the future, if we want to support it, just change the view of the deploy dialog
    """
    if server.driver != 'lenovo_xclarity':
        return False
    
    #if the deploy status from xClarity is empty, we cannot deploy it
    #in the future, the admin and other users may have different scope in deploy action
    if server.provision_state != '' and server.provision_state is not None and server.provision_state!='Not Ready':
        return True
    return False



def check_if_console_auth_allowed(server):
    """
    check if console auth pop up dialog needed
    for non lenovo_xclarity driver, we need to input the driver info(ipmi info)
    """
    if server.driver != 'lenovo_xclarity':
        return False
    return True

def check_if_reboot_allowed(server):
    """
    check if reboot allowed, this should be changed
    """
    if server.readyCheck and server.readyCheck['accessState']!='Offline':
        return True
    return False


def check_if_shutdown_allowed(server):
    """
    check if shutdown allowed, this should be changed
    """
    if server.readyCheck and server.readyCheck['accessState']!='Offline' and server.power_state == 'power on':
        return True
    return False

def check_if_poweron_allowed(server):
    """
    check if poweron allowed, this should be changed
    """
    if server.readyCheck and server.readyCheck['accessState']!='Offline' and server.power_state == 'power off':
        return True
    return False


def check_if_apply_allowed(server):
    """
    check if apply allowed
    """
    if server and server.applied != '0':
        return False
    return True

def check_if_public_allowed(server):
    """
    check if public allowed
    """
    if server and server.applied=='0':
        return False
    return True














