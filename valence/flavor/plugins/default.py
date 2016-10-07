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
import re
from oslo_log import log as logging
from valence.flavor.generatorbase import generatorbase

LOG = logging.getLogger()

class defaultGenerator(generatorbase):
    def __init__(self, nodes):
      generatorbase.__init__(self, nodes)

    def description(self):
      return "Generates 3 flavors(Tiny, Medium, Large) for each node considering all cpu cores, ram and storage"

    def generate(self):
      LOG.info("Default Generator")
      for node in self.nodes:
        LOG.info("Node ID " + node['nodeid'])
        location = node['location']
        #Systems:Rack1-Block1-Sled2-Node1_Sled:Rack1-Block1-Sled2_Enclosure:Rack1-Block1_Rack:Rack1_
        location_lst = location.split("_");
        location_lst = list(filter(None, location_lst))
        extraspecs = { l[0] : l[1] for l in (l.split(":") for l in location_lst) }
        name = self.prepend_name + location
      return {
        self._flavor_template("L_" + name, node['ram'] , node['cpu']["count"], node['storage'], extraspecs),
        self._flavor_template("M_" + name, int(node['ram'])/2 , int(node['cpu']["count"])/2 , int(node['storage'])/2, extraspecs),
        self._flavor_template("S_" + name, int(node['ram'])/4 , int(node['cpu']["count"])/4 , int(node['storage'])/4, extraspecs)
	  }
