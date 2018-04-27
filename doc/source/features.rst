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

.. _valence-features:

******************
Feature Highlights
******************

Valence provides the following capabilities for managing disaggregated hardware resources.

.. _multi-podm-support:

Multiple Podmanager Support
---------------------------

Valence provides the capability to manage multiple podmanagers.
Each podmanager can be configured to use different driver. By default,
``redfishv1`` driver is used.

Currently supported drivers in Valence are:
 #. :ref:`redfishv1-driver`
 #. :ref:`expether-driver`

Future work include redfish v2 driver support. Other vendors also could implement
their own driver to manage their hardware.

This provides uniform interface to manage all the disaggregated hardware in datacentre
supporting different protocols.

.. _device-orchestration:

Device Orchestration framework
------------------------------

Valence provides support for the dynamic management of pooled resources like storage,
network and other pci devices which can be connected on demand to a composed node,
giving user the ability to attach or detach the devices dynamically based on workload.

.. _ironic-provision-driver:

Ironic provision driver
-----------------------

Valence supports ``ironic`` provision driver to be able to register the valence composed
node to ironic. Once the node is registered further operations of provisioning/managing
could be directly performed using Ironic_.

For more details on Ironic usage:
`Ironic API guide <https://developer.openstack.org/api-ref/baremetal/>`_.


For more features please refer the Valence blueprints_ for supported and
in-the-pipeline features.

.. _blueprints: https://blueprints.launchpad.net/openstack-valence
.. _Ironic: https://docs.openstack.org/ironic/latest/
