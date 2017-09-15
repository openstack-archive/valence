=========================
Openstack Valence Project
=========================

Valence is a service for lifecycle management of pooled bare-metal hardware
infrastructure such as Intel(R) Rack Scale architecture which uses Redfish(TM)
as one of the management protocols.

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
valence-ui makes us of React.js javascript libaray and invoke Valence REST APIs through ajax REST calls.

========
Features
========
Please refer the Valence blueprints for supported and in-the-pipeline features.
``https://blueprints.launchpad.net/openstack-valence``
