=========================
Valence 0.9 Release Notes
=========================

*************
Main Features
*************

Multi-Podmanager Support
------------------------

Valence provides the capability to manage multiple podmanagers.
Each podmanager can be configured to use different driver.
By default valence provides redfish driver to manage the hardware.
Also provides framework for other vendors could implement their
own driver to manage their hardware.

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

Valence supports ironic provision driver to interface with Ironic, to be able to
register the valence composed node to ironic. Once the node is registered further
operations of provisioning/managing could be directly performed using Ironic.

More detail about :ref:`Ironic Provision Driver <ironic-provision-driver>`.

ExpEther driver
---------------

Added ExpEther driver support inside valence to be able to manage
NEC ExpEther hardware.

More detail about :ref:`ExpEther Driver <expether-driver>`.
