..
      Copyright (c) 2018 NEC, Corp.
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

.. _expether-driver:

===============
ExpEther Driver
===============

Overview
========

The ``ExpEther`` driver enables management of ExpEther Hardware through
Openstack Valence. It relies on EEM REST API to communicate to hardware.

For more details on hardware, please refer ExpEther_.

Prerequisites
=============

ExpEtherManager(EEM) should be configured and reachable from the controller.
It can be installed on node different from Openstack Controller.

``hwdata`` package is used to fetch PCI device details (vendor name,
device name) in human readable format. Retrieval of details is only
supported for 40g devices. If package is not available, the same
are shown as None.

For ubuntu, package can be installed using following command::
   $ sudo apt-get install hwdata

Supported Functionalities
=========================

* To be able to use the driver, first the podmanager needs to be created
  with connection information of the EEM service.

  The details needed for the same are:

  - EEM REST URL : http://<ip>:<port>/eem
  - Authentication Information (username/password)
  - driver : 'expether'

  To register the same please refer :ref:`example <create-pod-manager>`

* Once the podmanager is created, the same will be used for subsequent requests
  to communicate with hardware.

* Using ``expether`` driver the following functionalities are supported in Valence:

  #. Node Management, Server can be composed as per user requested flavor or
     the existing node can be made to be managed by Valence.
     Currently, for composing node, only supported flavor keys are ``pci_device``.
     Please refer :ref:`sample request <compose-node>`
  #. All the IO devices would be automatically discovered by the podmanager and
     would be managed by Valence. Also supports allocation of PCI devices from the
     resource pool to node as per workload demand.
     EE node managed by valence can be assigned from the pool of devices as per
     user request and the same will be released to pool once the workload decreases.
  #. Periodic discovery of all resources from podmanager is supported,
     which registers any newly connected resources to valence and keeps the status sync
     with podmanager and valence DB.
  #. Nodes managed by Valence can be made available to Ironic, for further provisioning using
     ironic provision driver supported in valence. For more details
     refer :ref:`ironic-provision-driver` and :ref:`sample request <node-register>`

Sample Requests
===============

.. _create-pod-manager:

Create a pod_manager
--------------------

Create a new podmanager connecting to ExpressEther Manager.

Sample request:

.. code-block:: bash

    curl -i -X POST "http://localhost:8181/v1/pod_managers" \
      -d '{"url": "http://<ip>:<port>/eem", "name": "podm1", \
      "driver": "expether", "authentication": [{"type": "basic", \
      "auth_items": {"username": "xxx", "password": "xxxx"}}]}' \
      -H "Accept:application/json" -H "Content-Type:application/json"

Response:

.. code-block:: json

    {
      "authentication": [
        {
          "auth_items": {
            "password": "xxx",
            "username": "xxx"
          },
          "type": "basic"
        }
      ],
      "created_at": "2018-04-20 04:40:01 UTC",
      "driver": "expether",
      "name": "podm1",
      "status": "Online",
      "updated_at": "2018-04-20 04:40:01 UTC",
      "url": "http://<ip>:<port>/eem",
      "uuid": "da5b1fba-e8bb-42be-baff-66ccb74087aa"
    }

.. _compose-node:

Compose a node
--------------

#. Using properties:

   Only flavor key supported is ``pci_device``.
   Example: {"pci_device": {"type": ["NIC"]}}

   Sample request:

   .. code-block:: bash

       curl -i -X POST "http://localhost:8181/v1/nodes" \
         -d '{"podm_id": "00000000-0000-0000-0000-000000000000", \
         "name": "node1", "properties": {"pci_device": {"type": ["NIC"]}}}' \
         -H "Accept:application/json" -H "Content-Type:application/json"

   Response:

   .. code-block:: json

       {
         "index": "0x000000000000",
         "name": "node1",
         "resource_uri": "devices/0x000000000000",
         "uuid": "bf28249c-a903-4ea9-a440-1ab28b0dab55"
       }

#. Using flavor:

   Sample request:

   .. code-block:: bash

     curl -i -X POST "http://localhost:8181/v1/nodes" \
        -d '{"podm_id": "00000000-0000-0000-0000-000000000000", \
        "name": "node1", "flavor_id": "11111111-1111-1111-1111-111111111111"}' \
        -H "Accept:application/json" -H "Content-Type:application/json"

   Response:

   .. code-block:: json

     {
       "index": "0x000000000000",
       "name": "node1",
       "resource_uri": "devices/0x000000000000",
       "uuid": "1ed6bba0-6354-4f57-aa61-09c15d5955bb"
     }

Manage a node
-------------

Register existing node to valence.

Sample request:

.. code-block:: bash

  curl -i  -g -X POST "http://localhost:8181/v1/nodes/manage" \
    -d '{"podm_id": <podm_id>, \
    "node_index": <node-index>}' \
    -H "Accept:application/json" -H "Content-Type:application/json"

Response:

.. code-block:: json

  {
    "index": "0x8cdf9d535b14",
    "name": "0x8cdf9d535b14",
    "resource_uri": "devices/0x8cdf9d535b14",
    "uuid": "2eebc520-7035-4797-a4ba-3b3dee2ea266"
  }

List devices
------------

List all resources.

Sample request:

.. code-block:: bash

  curl -i -X GET "http://localhost:8181/v1/devices" \
    -H "Accept:application/json" -H "Content-Type:application/json"

Response:

.. code-block:: json

  [
    {
      "node_id": "0x000000000000",
      "podm_id": "da5b1fba-e8bb-42be-baff-66ccb74087aa",
      "pooled_group_id": "1234",
      "resource_uri": "devices/1x111111111111",
      "state": "allocated",
      "type": "SSD",
      "uuid": "d38b2987-02f1-44c1-bdb6-c5469581d244"
    },
    {
      "node_id": null,
      "podm_id": "da5b1fba-e8bb-42be-baff-66ccb74087aa",
      "pooled_group_id": "4093",
      "resource_uri": "devices/2x222222222222",
      "state": "free",
      "type": "NIC",
      "uuid": "f3f57251-4213-487d-a471-8a2e5b1e18e4"
    }
  ]

Attach/detach a device to node
------------------------------

Attach a resource to node.

Sample request:

.. code-block:: bash

  curl -i -X POST "http://localhost:8181/v1/nodes/<node_id>/action" \
    -d '{"attach": {"resource_id": "<resource_id>"}}' \
    -H "Accept:application/json" -H "Content-Type:application/json"

Response:

.. code-block:: console

  204 NO CONTENT

Detach a resource to node.

Sample request:

.. code-block:: bash

  curl -i -X POST "http://localhost:8181/v1/nodes/<node_id>/action" \
    -d '{"detach": {"resource_id": "<resource_id>"}}' \
    -H "Accept:application/json" -H "Content-Type:application/json"

Response:

.. code-block:: console

  204 NO CONTENT

.. _node-register:

Node register
-------------

Register node with ironic.

Sample request:

.. code-block:: bash

  curl -i -X POST \
   "http://localhost:8181/v1/nodes/bd412ef8-d49e-46f3-a7dd-9879a7435dc9/register" \
   -d '{"driver_info": {"username":"admin","password":"password", \
   "address":"address"}}' \
   -H "Accept:application/json" -H "Content-Type:application/json"

Response:

.. code-block:: json

  {
     "created_at": "2018-04-20 04:40:01 UTC",
     "index": "0x000000000000",
     "managed_by": "ironic",
     "name": "node1",
     "podm_id": "da5b1fba-e8bb-42be-baff-66ccb74087aa",
     "resource_uri": "devices/0x000000000000",
     "updated_at": "2018-04-20 04:40:01 UTC",
     "uuid": "1ed6bba0-6354-4f57-aa61-09c15d5955bb"
  }

.. _ExpEther: http://www.expether.org/
