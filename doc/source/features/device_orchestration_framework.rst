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

.. _device_orchestration_framework:

==============================
Device Orchestration framework
==============================

Overview
========

This feature provides efficient way of managing pooled resources, being able
to dynamically assign or remove resources from the composed node on th fly
(based on the workload). The result of this is providing optimal usage of the
resources.

Concepts
========

.. _added_device_db_entry:

Added devices table in DB
-------------------------

A new table named ``devices`` added to valence DB, which stores all the
information regarding all devices connected to podmanagers.

.. _sync_devices:

Device Synchronization
----------------------

Synchronize devices of podmanager with the valence DB. This is done in
following ways.

- ``Periodic sync`` Sync devices periodically in background on application
  startup.
- ``One time sync`` User can make this request using simple API request.
- Also, while podmanager creation sync of connected devices happens in
  background

.. _added_apis:

Added new apis in Valence
-------------------------

This feature has implemented new apis in valence as follows:

#. List Devices
#. Show Device
#. Sync Devices
#. Node action attach/detach
