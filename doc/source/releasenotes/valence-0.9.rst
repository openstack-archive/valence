=============
Release Notes
=============

*************
Main Features
*************

Multi-Podmanager Support
------------------------

Added framework in valence for management of multiple pod managers
which can be from different vendors using respective drivers.
By default valence provides redfish driver to manage the hardware.

More detail refer :ref:`Multi Podmanager Support <multi-podm-support>`.

Device Orchestration
--------------------

Valence supports management of pooled resources and adds
ability to attach/detach dynamically to nodes according
to workload demand. New config option 'enable_periodic_sync'
supported to sync resources from podmanager periodically.
By default, periodic sync is disabled.

More detail about :ref:`Device Orchestration Framework <device-orchestration>`.

Ironic provision driver
-----------------------

Valence is able to communicate with Openstack-Ironic and able to register
the composed nodes for baremetal provisioning via ironic.

More detail about :ref:`Ironic Provision Driver <ironic-provision-driver>`.

ExpEther driver
---------------

Added ExpEther driver support inside valence to be able to manage
NEC ExpEther hardware.

More detail about :ref:`ExpEther Driver <expether-driver>`.
