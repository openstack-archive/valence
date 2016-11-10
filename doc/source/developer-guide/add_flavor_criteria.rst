.. _add_flavor_criteria:
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

In this Guide, you will find information on how to create a new
'flavor criteria plugin' in Valence.
Every flavor criteria pluin implements a particular logic to generate
flavors based on the hardware details obtained from PODM. These plugins
could be invoked seperately or collectively through REST APIs.
This guide assumes that Valence environment is already setup
(if not please go through the `readme.rst`).


Flavors
-------

Openstack by default provides flavors for deploying VMs e.g. m1.Tiny, m1.Small..etc.
In valence, since we already know the hardware details obtained from PODM,
flavors could be generated to match the hardware. These flavors could be used by
Openstack to deploy VMs.

Flavor Criteria
---------------

'Criteria', represents the aspect on which the flavor generation logic depends on.
The Flavor criteria could be CPU, location of hardware, storage, RAM, network interfaces ..etc.
These are implemented as plugins such that new criteria could be added/removed dynamically.

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

The above example shows only one criteria .i.e 'cpu', Which means that there are only one plugin
available.


Adding a New Criteria Plugin
----------------------------

Before starting to implement, here are some useful details

- All the implementation that handles "Flavor" are inside valence/flavor module.

- The plugin loading mechanisms are inside valence/flavor.py

- All the python files(except __init__.py) inside the flavor plugins path
  (valence/flavor/plugins) are considered as plugins.

- The name of the plugin file is the name of "Criteria" i.e. to invoke that plugin one
  have to pass the filename as Criteria name.

- Every plugin must implement the abstract methods declared in the generatorbase class.
  The generatorbase class is defined in valence/flavor/generatorbase.py

- Every plugin has a property(self.nodes) which contains the list of dictionaries of composed node
  details .i.e node id, uuid, hardware details, location ..etc.

Lets see how to implement a flavor criteria plugin.
Assume, we are going to create an example flavor criteria plugin called "examplecpu_core"
that generates one flavor for each node based on the number of CPU cores.

#. Copy the valence/flavor/plugins/example.py file as examplecpu_core.py
   i.e. the class name should be examplecpu_core + ‘Generator’ = examplecpu_coreGenerator

#. Implement the abstract methods description() & generate().

   ``description()`` : Function that describes the nature of the plugin

   ``generate()``    : Function that generates and returns the flavors in standard
                       "openstack flavor json format"

   In the plugin generate() function, put the below implementation. It simply loops
   through all the nodes and generates one flavor for each node.

        .. code-block:: python

             def description(self):
                 return "My first Flavor plugin based on CPU Core count"

             def generate(self):
                 LOG.info("Example CPU Core count Flavor Generator")
                 for node in self.nodes:
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
                   "name": "examplecpu_core",
                   "description": "My first Flavor plugin based on CPU Core count"
                }]
             }

   * POST /v1/flavor - To generate flavor from our newly created plugin

        .. code-block:: bash

           $ curl –d  { "criteria": "examplecpu_core"} -H "Content-Type: application/json"
             http://localhost:8181/v1/flavor

        response:

        .. code-block:: json

              [[
                 {"flavor ": {"disk ": 10, "vcpus ": 1, "ram ": 16,
                               "name ": "S_irsd - Rack1Block1 ",
                               "id ":"321a271-ab30-4dfb-a098-6cfb8549a143"}},
                               "extra_specs": {}
             ]]


#. Update the automated testing scripts to include the new API.
   (Please refer functional testing document)
