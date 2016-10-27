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

from ironic.common.i18n import _
from ironic import objects
from ironic.common import exception
from ironic.common import states
from ironic.drivers.modules.rsa_podm import constants

PODM_REQUIRED_PROPERTIES = {
    'podm_ip': _('IP address of the podm. Required.'),
    'podm_username': _('username used for authentication. Required.'),
    'podm_password': _('password used for authentication. Required.'),
    'podm_protocol': _('protocol used by podm connection, default is https')
}


def parse_podm_driver_info(node):
    """
    Parses the podm driver_info of the node, reads default values
    and returns a dict containing the combination of both.

    :param node: an ironic node object.
    :returns: a dict containing information from driver_info
              and default values.
    :raises: InvalidParameterValue if some mandatory information
             is missing on the node or on invalid inputs.
    """

    driver_info = node.driver_info
    parsed_driver_info = {}

    error_msgs = []
    for param in PODM_REQUIRED_PROPERTIES:
        try:
            parsed_driver_info[param] = str(driver_info[param])
        except KeyError:
            error_msgs.append(
                _("'%s' not supplied to RSA POD Manager Driver.") % param)
        except UnicodeEncodeError:
            error_msgs.append(_("'%s' contains non-ASCII symbol.") % param)

    try:
        parsed_driver_info['podm_protocol'] = str(
            driver_info.get('podm_protocol', 'https'))
    except UnicodeEncodeError:
        error_msgs.append(_("'podm_protocol' contains non-ASCII symbol."))

    if error_msgs:
        msg = (_(
            'The following errors were encountered while parsing '
            'driver_info:\n%s') % '\n'.join(error_msgs))
        raise exception.InvalidParameterValue(msg)

    return parsed_driver_info


def get_powerstatus_from_statuscode(status):
    if str(status) == constants.PODM_POWER_ON_CODE:
        return states.POWER_ON
    elif str(status) == constants.PODM_POWER_OFF_CODE:
        return states.POWER_OFF
    else:
        return states.ERROR


def check_exist_in_db(context, physical_uuid, nodelist):
    """
    physical uuid is a property in extra
    uuid and instance_uuid is a property of node

    :param nodelist:
    :param physical_uuid:
    :param context:
    """
    for db_node in nodelist:
        if db_node.extra['physical_uuid'] == physical_uuid:
            return objects.Node.get_by_uuid(context, db_node['uuid'])
    return None
