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
from rsc.flavor.generatorbase import generatorbase

LOG = logging.getLogger()

class assettagGenerator(generatorbase):
    def __init__(self, nodes):
      generatorbase.__init__(self, nodes)

    def description(self):
      return "Demo only: Generates location based on assettag"

    def generate(self):
      LOG.info("Default Generator")
      for node in self.nodes:
        LOG.info("Node ID " + node['nodeid'])
        location = node['location']
        location = location.split('Sled')[0]
        #Systems:Rack1-Block1-Sled2-Node1_Sled:Rack1-Block1-Sled2_Enclosure:Rack1-Block1_Rack:Rack1_
        location_lst = re.split("(\d+)", location)
        LOG.info(str(location_lst))
        location_lst = list(filter(None, location_lst))
        LOG.info(str(location_lst))
        extraspecs = {location_lst[i]: location_lst[i+1] for i in range(0,len(location_lst),2)}
        name = self.prepend_name + location
      return {
        self._flavor_template("L_" + name, node['ram'] , node['cpu']["count"], node['storage'], extraspecs),
        self._flavor_template("M_" + name, int(node['ram'])/2 , int(node['cpu']["count"])/2 , int(node['storage'])/2, extraspecs),
        self._flavor_template("S_" + name, int(node['ram'])/4 , int(node['cpu']["count"])/4 , int(node['storage'])/4, extraspecs)
	  }
