=========================
Openstack Valence Project
=========================

Valence is a service for lifecycle management of pooled bare-metal hardware
infrastructure which uses vendor specific drivers to interact with the
dis-aggregated resources from respective vendors such as Intel(R) Rack Scale
architecture which uses Redfish(TM), NEC developed Express Ether hardware
which uses expether driver as management protocols.

:Free software: Apache license
:Wiki: https://wiki.openstack.org/wiki/Valence
:Source: http://git.openstack.org/cgit/openstack/valence
:Bugs: https://bugs.launchpad.net/openstack-valence


=========================
Download and Installation
=========================

The following steps capture how to install valence. All installation steps
require super user permissions.

**************************
Database etcd installation
**************************

 Single node installation reference: https://github.com/coreos/etcd/releases

 Distributed installation reference: https://github.com/coreos/etcd/blob/master/Documentation/op-guide/clustering.md

 For development, single node installation is recommended practice.

********************
Valence installation
********************

 1. Install software dependencies

    ``$ sudo apt-get install git python-pip python-dev build-essential``

 2. Clone the Valence code from git repo.

    ``$ git clone https://git.openstack.org/openstack/valence``

 3. Execute the 'install_valence.sh' file present in the Valence root directory.
    The install script will automatically install the dependencies listed in the
    requirements.txt file.

    ``$ sudo bash install_valence.sh``

 4. Check the values in valence.conf located at /etc/valence/valence.conf

    ``set the ip/credentials of podm for which this Valence will interact``

 5. Check the PYTHON_HOME and other variables in /etc/init/valence.conf

 6. Initialize etcd database

    ``$ valence-db-manager init``

    Note: The TypeError exception "TypeError: NoneType object is not callable"
    is caused by known python-etcd bug, which will not impact this db init
    functionality.
    https://github.com/jplana/python-etcd/issues/190

 7. Start valence service

    ``$ sudo service valence start``

 8. Logs are located at /var/logs/valence/

****************
GUI installation
****************
Please refer to the installation steps in the ui/README file.


**********
Components
**********

Valence follows the typical OpenStack project setup. The components are listed
below:

valence-api
-----------
A python based daemon based on Flask framework to expose Valence REST APIs.
The api service communicates to the PODM through REST interface using Redfish(TM) specification.
For adding new api please refer https://github.com/openstack/valence/blob/master/doc/source/developer-guide/add_new_api.rst

valence-ui
----------
valence-ui provides a Web-based GUI interface that can be used to explore
Rack Scale Design (RSD) artifacts and compose/disassemble nodes.
valence-ui is implemented using Node.js runtime environment and hosted through apache.
valence-ui makes us of React.js javascript library and invoke Valence REST APIs through ajax REST calls.

*************
Configuration
*************

The Valence service is configured via its configuration file. This file
is typically located at ``/etc/valence/valence.conf``.
Refer :ref:`valence-conf` for various options.

********
Features
********

Major features supported by valence are as following:

Multiple Podmanager Support
---------------------------

This feature helps in integrating all podmanagers from different vendors
i.e user doesn't need to deploy multiple valence for every podmanager.
It fills gap of switching between multiple podmanagers which is never easy
to manage different podmanager from every vendor. So, valence provide
convenient way to manage all podmanagers.

Vendor Extensible framework
---------------------------

This feature provides multiple vendors to manage their dis-aggregated
resources via valence. Vendors using drivers other than redfish can simply
add their driver in valence and manage their hardware.

Concepts
~~~~~~~~

A new field ``driver`` is added to podmanager, which user need to mention
while creating a podmanager. The mentioned driver will load respective
podmanager that will be vendor specific.

.. NOTE::
    By default it will select ``redfishv1`` driver

Device Orchestration framework
------------------------------

This feature provides efficient way of managing pooled resources, being able
to dynamically assign or remove resources from the composed node on th fly
(based on the workload). The result of this is providing optimal usage of the
resources.

Concepts
~~~~~~~~

#. Added devices table in DB

   A new table named ``devices`` added to valence DB, which stores all the
   information regarding all devices connected to podmanagers.

#. Device Synchronization

   Synchronize devices of podmanager with the valence DB. This is done in
   following ways.

   - ``Periodic sync`` Sync devices periodically in background on application
     startup.
   - ``One time sync`` User can make this request using simple API request.
   - Also, while podmanager creation sync of connected devices happens in
     background

.. _ironic-provision-driver:

Ironic provision driver
-----------------------

This feature provides user an ability to register node in Ironic_
i.e composed node in valence having required configuration can be registered
to Openstack-Ironic from valence. Further provisioning of node can be done using:
`Ironic API guide <https://developer.openstack.org/api-ref/baremetal/>`_.

Added new apis in Valence
-------------------------

This feature has implemented new apis in valence as follows:

#. List Devices
#. Show Device
#. Sync Devices
#. Node action attach/detach

For more features please refer the Valence blueprints_ for supported and
in-the-pipeline features.

.. _blueprints: https://blueprints.launchpad.net/openstack-valence
.. _Ironic: https://docs.openstack.org/ironic/latest/
