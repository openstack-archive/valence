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

.. _vendor_extensible_framework:

===========================
Vendor Extensible framework
===========================

Overview
========

This feature provides multiple vendors to manage their dis-aggregated
resources via valence. Vendors using drivers other than redfish can simply
add their driver in valence and manage their hardware.

Concepts
========

A new field ``driver`` is added to podmanager, which user need to mention
while creating a podmanager. The mentioned driver will load respective
podmanager that will be vendor specific.

.. NOTE::
    By default it will select ``redfishv1`` driver
