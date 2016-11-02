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

from importlib import import_module
import logging
import os
from valence.redfish import redfish as rfs

FLAVOR_PLUGIN_PATH = os.path.dirname(os.path.abspath(__file__)) + '/plugins'
LOG = logging.getLogger(__name__)


def get_available_criteria():
    pluginfiles = [f.split('.')[0]
                   for f in os.listdir(FLAVOR_PLUGIN_PATH)
                   if os.path.isfile(os.path.join(FLAVOR_PLUGIN_PATH, f))
                   and not f.startswith('__') and f.endswith('.py')]
    resp = []
    for p in pluginfiles:
        module = import_module("valence.flavor.plugins." + p)
        myclass = getattr(module, p + 'Generator')
        inst = myclass([])
        resp.append({'name': p, 'description': inst.description()})
    return {'criteria': resp}


def create_flavors(data):
    """criteria : comma seperated generator names

       This should be same as thier file name)

    """
    criteria = data["criteria"]
    respjson = []
    lst_systems = rfs.systems_list()
    LOG.info("aaaaa")
    for g in criteria.split(","):
        if g:
            LOG.info("Calling generator : %s ." % g)
            module = __import__("valence.flavor.plugins." + g, fromlist=["*"])
            classobj = getattr(module, g + "Generator")
            inst = classobj(lst_systems)
            respjson.append(inst.generate())
    return respjson
