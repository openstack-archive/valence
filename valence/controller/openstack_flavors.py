# Copyright (c) 2016 Intel, Inc.
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
#    under the License.

import json
import logging

from novaclient import client
import valence.conf
from valence.controller import nodes
from valence.db import api as db_api

LOG = logging.getLogger(__name__)
CONF = valence.conf.CONF


def convert_data_type(value, datatype):
    if datatype is int:
        return int(value)
    elif datatype is float:
        return float(value)
    elif datatype is long:
        return long(value)


def get_node_field(field_name, node_spec):
    for key, value in node_spec.items():
        if key == field_name:
            return value
        else:
            node_field = None
        if isinstance(value, list):
            for k in value:
                node_field = get_node_field(field_name, k)
        elif isinstance(value, dict):
                node_field = get_node_field(field_name, value)
        if node_field:
            break
    return node_field


def check_spec(node_spec, extra_spec_value, noparams):
    for key, value in node_spec.items():
        if isinstance(value, list):
            for k in value:
                satisfies_spec, found_key = check_spec(k,
                                                       extra_spec_value,
                                                       noparams)
        elif isinstance(value, dict):
            satisfies_spec, found_key = check_spec(value,
                                                   extra_spec_value,
                                                   noparams)
        else:
            if key in extra_spec_value.keys():
                noparams = noparams - 1
                found_key = True
                satisfies_spec = False
                if (isinstance(value, str)):
                    if (value == str(extra_spec_value.get(key))):
                        satisfies_spec = True
                        if noparams == 0:
                            return satisfies_spec, found_key
                    else:
                        return satisfies_spec, found_key
                elif (isinstance(value, unicode)):
                    if (value == unicode(extra_spec_value.get(key))):
                        satisfies_spec = True
                        if noparams == 0:
                            return satisfies_spec, found_key
                    else:
                        return satisfies_spec, found_key
                elif (value >= convert_data_type(
                      (extra_spec_value.get(key)), type(value))):
                    satisfies_spec = True
                    if noparams == 0:
                        return satisfies_spec, found_key
                else:
                        return satisfies_spec, found_key
            else:
                found_key = False
                satisfies_spec = False
        if ((found_key and (not satisfies_spec)) or (noparams == 0)):
            break
    return satisfies_spec, found_key


def check_spec_key(node_spec, extra_spec_key, extra_spec_value):
    for key, value in node_spec.items():
        if key == extra_spec_key:
            found_key = True
            satisfies_spec = False
            if (isinstance(value, str)):
                if (value == str(extra_spec_value)):
                    satisfies_spec = True
            elif isinstance(value, unicode):
                if (value == unicode(extra_spec_value)):
                    satisfies_spec = True
            elif (value >= convert_data_type(extra_spec_value,
                                             type(value))):
                satisfies_spec = True
            return satisfies_spec, found_key
        else:
            found_key = False
            satisfies_spec = False
    return satisfies_spec, found_key


def create_flavor(values):
    extra_spec = values.get('extra_specs')
    flavor_created = False
    nodelist = [n.get('uuid') for n in nodes.Node.list_composed_nodes()]
    for n in nodelist:
        node_spec = nodes.Node.get_composed_node_by_uuid(n)
        for key in extra_spec.keys():
            if isinstance(extra_spec.get(key), dict):
                resp = get_node_field(key, node_spec)
                if not resp:
                    return ("invalid key '" + key + "' specified in"
                            + " extra_specs")
                else:
                    new_node_spec = {key: resp}
                    resp, fnd_key = check_spec(new_node_spec,
                                               extra_spec.get(key),
                                               len(extra_spec.get(key).keys()))
                if not fnd_key:
                    return ("invalid key specified in dictionary "
                            + json.dumps(extra_spec.get(key)) +
                            " in extra_specs")
            else:
                resp, fnd_key = check_spec_key(node_spec, key,
                                               extra_spec.get(key))
                if not fnd_key:
                    return ("invalid key '" + key + "' specified in"
                            + " extra_specs")
            if not resp:
                break
        if resp:
            flavor = db_api.Connection.create_openstack_flavor(values)
            flavor_created = True
            return flavor.as_dict()
    if not flavor_created:
        return "Failed to create flavor as no node satisfies extra_specs"


def list_flavors():
    flavor_models = db_api.Connection.list_openstack_flavors()
    return [flavor.as_dict() for flavor in flavor_models]


def register(flavoruuid):
    flavor = (db_api.Connection.get_openstack_flavor_by_uuid(flavoruuid).
              as_dict())
    d = dict()
    d['version'] = CONF.openstack.nova_api_version
    d['username'] = CONF.openstack.username
    d['password'] = CONF.openstack.password
    d['auth_url'] = CONF.openstack.auth_url
    d['project_name'] = CONF.openstack.project_name
    d['user_domain_id'] = CONF.openstack.user_domain_id
    d['project_domain_id'] = CONF.openstack.project_domain_id

    nova = client.Client(**d)
    data = flavor
    name = data.get("name")
    ram = data.get("ram")
    vcpus = data.get("vcpus")
    disk = data.get("disk")
    extra_specs = data.get("extra_specs")
    extra_specs_new = dict()
    for key in extra_specs.keys():
        if isinstance(extra_specs.get(key), dict):
            obj = extra_specs.get(key)
            for k, v in obj.items():
                nkey = key + "_" + k
                extra_specs_new.update({nkey: v})
        else:
            extra_specs_new.update({key: extra_specs.get(key)})
    cflavor = nova.flavors.create(name, ram, vcpus, disk)
    cflavor.set_keys(extra_specs_new)
    return "Flavor successfully added to openstack"


def show_flavor(flavoruuid):
    flavor = (db_api.Connection.get_openstack_flavor_by_uuid(flavoruuid).
              as_dict())
    return flavor


def delete_openstack_flavor(flavoruuid):
    db_api.Connection.delete_openstack_flavor(flavoruuid)
    return "Flavor deleted successfully"
