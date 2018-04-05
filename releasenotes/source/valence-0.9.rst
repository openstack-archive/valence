===================
Valence 0.9 Release
===================

*************
Main Features
*************

Support for multi-vendors in Valence
------------------------------------

Added framework in valence for different vendors to plugin their
driver to manage the dis-aggregated hardware. By default valence
provides redfish driver to manage the hardware.
More detail refer :ref:`Multi Podmanager Support <multi-podm-support>`.

Device Orchestration
--------------------

Valence supports management of pooled resources and adds
ability to attach/detach dynamically to nodes according
to workload demand. New config option 'enable_periodic_sync'
supported to sync resources from podmanager periodically.
By default, periodic sync is disabled.
More detail about :ref:`Device Orchestration Framework <device-orchestration>`.

ExpEther driver
---------------

Added ExpEther driver support inside valence to be able to manage
NEC ExpEther hardware.
More detail about :ref:`ExpEther Driver <expether-driver>`.
