=========================
Openstack Valence Project
=========================

********
Overview
********

Valence is a service for lifecycle management of pooled bare-metal hardware
infrastructure.  The concept of pooled storage (SSDs or nvmE) disaggregated
from compute nodes and network disaggregated from compute and storage
provides the flexibility to compose and uses as and when the cloud requires
more server resources. Valence provides the capability "compose" hardware nodes
and release resources as needed by the overcloud.

Valence supports Redfish as default management protocol to communicate
to hardware. It supports Rack Scale Design (RSD), Open architecture for management
of disaggregated server hardware resources, which is standardized in Redfish.
Valence also provides capability to manage other vendors disaggregated hardware
using their respective drivers other than Redfish.

:Free software: Apache license
:Wiki: https://wiki.openstack.org/wiki/Valence
:Source: http://git.openstack.org/cgit/openstack/valence
:Bugs: https://bugs.launchpad.net/openstack-valence

.. _valence-features:

******************
Feature Highlights
******************

Valence provides the following capabilities for managing disaggregated hardware resources.

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
