..
      Copyright (c) 2017 NEC, Corp.
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

.. _expether_driver:

===============
ExpEther Driver
===============

Overview
========

The ``ExpEther`` driver enables management of hardware compliant with EEM
(ExpressEtherManager). Visit ExpEther_ website for more details.
In this document, you will find information on how to use ExpEther via Valence.
This document assumes that Valence environment is already setup (if not please go
through the `readme.rst`).

Prerequisites
=============

* ExpressEtherManager should be configured on the system.

* Package Python-hwdata_ should be installed on system to fetch PCI device
  details in human readable format

Usage
=====

Create a pod_manager
--------------------

Create a new podmanager connecting to ExpressEther Manager using
   * EEM url, for example: http://0.0.0.0:00000/eem
   * Name of podmanager
   * Username and password to connect to EEM
Sample request:
   .. code-block:: bash

      curl -i -X POST "http://localhost:8181/v1/pod_managers" \
        -d '{"url": "http://0.0.0.0:00000/eem", "name": "podm1", \
        "driver": "expether", "authentication": [{"type": "basic", \
        "auth_items": {"username": "admin", "password": "eemeem"}}]}' \
        -H "Accept:application/json" -H "Content-Type:application/json"
.. NOTE::
         Do not add '/' in the end of url


Compose a node
--------------

Compose a node using
   * Podmanager id
   * Name
   * Properties/Flavor_id, for example: {"pci_device": {"type": ["NIC"]}}
Sample request:
   .. code-block:: bash

      curl -i -X POST "http://localhost:8181/v1/nodes" \
        -d '{"podm_id": "00000000-0000-0000-0000-000000000000", \
        "name": "node1", "properties": {"pci_device": {"type": ["NIC"]}}}' \
        -H "Accept:application/json" -H "Content-Type:application/json"


Manage a node
-------------

Manage a node using
   * Podmanager id
   * EESV id
Sample request:
   .. code-block:: bash

      curl -i  -g -X POST "http://localhost:8181/v1/nodes/manage" \
        -d '{"podm_id": "00000000-0000-0000-0000-000000000000", \
        "node_index": "0x000000000000"}' \
        -H "Accept:application/json" -H "Content-Type:application/json"


List devices
------------

List all devices using following sample request
Sample request:
   .. code-block:: bash

      curl -i -X GET "http://localhost:8181/v1/devices" \
        -H "Accept:application/json" -H "Content-Type:application/json"


Attach/detach a device to node
------------------------------

Attach/detach a device using
   * Node id
   * Resource id
   * Action i.e attach/detach
Sample request:
   .. code-block:: bash

      curl -i -X POST "http://localhost:8181/v1/nodes/<node_id>/action" \
        -d '{"detach": {"resource_id": "<resource_id>"}}' \
        -H "Accept:application/json" -H "Content-Type:application/json"


Enable periodic sync of devices
-------------------------------

To enable background synchronization of devices follow simple steps:
   * Set 'enable_periodic_sync' in /etc/valence/valence.conf to true
   * Set 'sync_interval' to interval value in seconds
   * Restart service

This will detect all the podmanagers and start syncing corresponding devices.

.. _ExpEther: http://www.expether.org/
.. _Python-hwdata: https://github.com/xsuchy/python-hwdata
