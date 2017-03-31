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

import logging

from keystoneauth1.identity import v3
from keystoneauth1 import session
from novaclient import client
import requests
from valence.db import api as db_api

LOG = logging.getLogger(__name__)

satisfies_spec = False
found_key = False


def check_spec(node_spec, extra_spec_key, extra_spec_value):
    global satisfies_spec
    global found_key
    for key, value in node_spec.items():
        if isinstance(value, list):
            for k in value:
                satisfies_spec, found_key = check_spec(k, extra_spec_key,
                                                       extra_spec_value)
        elif isinstance(value, dict):
            satisfies_spec, found_key = check_spec(value, extra_spec_key,
                                                   extra_spec_value)
        else:
            if key == extra_spec_key:
                found_key = True
                if value == extra_spec_value:
                    satisfies_spec = True
                    return satisfies_spec, found_key

    return satisfies_spec, found_key


def create_flavor(values):

    extra_spec = values['extra_specs']
    url = "http://10.223.197.160/"
    nodes = ["test3.json", "test4.json"]
    flavor_created = False
    for node in nodes:
        try:
            nurl = url + node
            resp = requests.request('GET', nurl, verify=False)
        except requests.exceptions.RequestException as e:
            LOG.error(e)
        resp = resp.json()
        resp = resp['node']
        node_spec = resp
        for key in extra_spec.keys():
            global satisfies_spec
            global found_key
            satisfies_spec = False
            found_key = False
            resp, fnd_key = check_spec(node_spec, key, extra_spec.get(key))
            if not resp:
                break

        if not fnd_key:
            return "invalid key specified in extra_specs while creating label"
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
    auth = v3.Password(auth_url='http://10.223.197.160:5000/v3',
                       username='admin',
                       password='openstack',
                       project_name='admin',
                       user_domain_id='default',
                       project_domain_id='default')
    sess = session.Session(auth=auth)
    nova = client.Client("2.1", session=sess)
    data = flavor
    name = data.get("name")
    ram = data.get("ram")
    vcpus = data.get("vcpus")
    disk = data.get("disk")
    extra_specs = data.get("extra_specs")
    cflavor = nova.flavors.create(name, ram, vcpus, disk)
    cflavor.set_keys(extra_specs)
    return "Flavor successfully added to openstack"


def show_flavor(flavoruuid):
    flavor = (db_api.Connection.get_openstack_flavor_by_uuid(flavoruuid).
              as_dict())
    return flavor


def delete_openstack_flavor(flavoruuid):
    db_api.Connection.delete_openstack_flavor(flavoruuid)
    return "Flavor deleted successfully"
