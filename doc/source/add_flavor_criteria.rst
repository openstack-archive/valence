..
      Copyright 2016 Intel Corporation
      All Rights Reserved.

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

=======================
Flavor Criteria Plugins
=======================

In this Guide, you will find information on how to create a new flavor criteria plugin in Valence. This guide assumes that Valence development environment is already setup (if not please go through the `readme.rst`). 


Flavors
-------

Openstack by default contains flavors for deploying VMs e.g. m1.Tiny, m1.Small, m1.Large..etc. likely based on the hardware details obtained from PODM, Valence generates 'Openstack Flavors' which could be used by Openstack to deploy VMs. 

Flavor Criteria
---------------

These flavors could be optimized to place the VMs on appropriate hardware for efficient utilization and need. 'Criteria', represents the aspect on which the flavor generation logic depends on.  The Flavor criteria could be CPU, location, storage ..etc. These are implemented as plugins such that new criteria could be added/removed dynamically.

To get the list of default "Criteria" implemented in Valence, you could do a GET
request to /v1/flavor

        .. code-block:: bash

           $ curl http://localhost:8181/v1/flavor

        response:

        .. code-block:: json

             {
                "criteria": [{
                   "name": "cpu",
                   "description": "Generates cpu  based flavors"
                }]
             }



Adding a New Criteria Plugin
----------------------------

Before starting to implement, here are some useful details

- All the implementations that handles "Flavor" are inside valence/flavor module.

- The plugin loading mechanisms are inside valence/flavor.py

- All the .py files inside the path valence/flavor/plugins are considered as plugins.

- The name of the plugin file is the name of "Criteria" i.e. to invoke that plugin one
  have to give the pass the filename as Criteria name.

- Every plugin must implement the 'generatorbase' class inside valence/flavor/generatorbase.py

- Every plugin has a property(self.nodes) which contains the list of node details
  .i.e node id, uuid, hardware details, location ..etc which are essential for flavors

Lets see how to implement a flavor criteria plugin.
Assume, we are going to create an example flavor criteria plugin called "examplecpu_core"
that generates one flavor for each node based on CPU cores.

#. Copy valence/flavor/plugins/example.py file as exampleone.py i.e. the class name should be exampleone + ‘Generator’ = exampleoneGenerator

#. Implement the abstract methods description() & generate().

   ``description()`` : Function that describes the nature of the plugin

   ``generate()``    : This function generates and returns the flavors in standard "openstack flavor json format"

   In the plugin generate() function, put the below implementation. It simply loops
   through all the nodes and generates one flavor for each node.

        .. code-block:: python

             def description(self):
                 return "My first Flavor plugin sample"

             def generate(self):
                 LOG.info("Default Generator")
                 for node in self.nodes:
                     LOG.info("Node ID " + node['id'])
                     extraspecs = {}
                     return {  self._flavor_template(node['id'],
                               node['ram'],
                               node['cpu']["count"],
                               node['storage'], extraspecs)
                            }


#. Deploy and restart the valence server

        .. include:: deploy.rst


#. Test the implementation.


   * GET /v1/flavor - This lists the newly created plugin

        .. code-block:: bash

           $ curl http://localhost:8181/v1/flavor

        response:

        .. code-block:: json

             {
                "criteria": [{
                   "name": "cpu",
                   "description": "Generates cpu  based flavors"
                }, {
                   "name": "exampleone",
                   "description": "My first Flavor plugin sample"           
                }]
             }

     * POST /v1/flavor - To generate flavor from our newly created plugin

        .. code-block:: bash

           $ curl –d  { "criteria": "plugin1"} -H "Content-Type: application/json"
             http://localhost:8181/v1/flavor

        response:

        .. code-block:: json

              [[
                 {"flavor ": {"disk ": 0, "vcpus ": 0, "ram ": 16,
                               "name ": "S_irsd - Rack1Block1 ",
                               "id ":"321a271-ab30-4dfb-a098-6cfb8549a143"}},
                               "extra_specs": {}
             ]]


#. Update the automated testing scripts to include the new API.
   (Please refere functional testing document )

