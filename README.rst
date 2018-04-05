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
could be directly performed using Ironic.

For more details on Ironic usage:
`Ironic API guide <https://developer.openstack.org/api-ref/baremetal/>`_.


For more features please refer the Valence blueprints_ for supported and
in-the-pipeline features.

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

Valence provides configuration file to configure Valence service specific to your requirements.
This file is typically located at ``/etc/valence/valence.conf``.
For the various config options supported, please refer :ref:`valence-conf`.

.. _blueprints: https://blueprints.launchpad.net/openstack-valence
.. _Ironic: https://docs.openstack.org/ironic/latest/
