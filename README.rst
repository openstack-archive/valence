=========================
Openstack Valence Project
=========================

Valence is a service for lifecycle management of pooled bare-metal hardware
infrastructure such as Intel(R) Rack Scale architecture which uses Redfish(TM)
as one of the management protocols.

:Free software: Apache license
:Wiki: https://wiki.openstack.org/wiki/Valence
:Source: http://git.openstack.org/cgit/openstack/rsc
:Bugs: http://bugs.launchpad.net/openstack-valence


===========================
Download and Installation
===========================

The following steps capture how to install valence. All installation steps
require super user permissions.

*******************************************
Valence installation
*******************************************

 1. Install software dependencies

    ``$ sudo apt-get install git python-pip``

 2. Clone the Valence code from git repo.

    ``$ git clone https://git.openstack.org/openstack/rsc``

 3. Execute the 'install_valence.sh' file present in the Valence root directory.
 The install script will automatically install the dependencies listed in the
 requirements.txt file.

    ``$ sudo bash install_valence.sh``

 4. Check the values in valence.conf located at /etc/valence/valence.conf

    ``set the ip/credentials of podm for which this Valence will interact``

 5. Check the PYTHON_HOME and other variables in /etc/init/valence.conf

 6. Start valence service

    ``$ sudo service valence start``

 7. Logs are located at /var/logs/valence/

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
A pecan based daemon to expose Valence REST APIs. The api service communicates
to the controller through AMQP.

valence-controller
--------------
The controller implements all the handlers for Plasma-api. It reads requests
from the AMQP queue, process it and send the reponse back to the caller.

valence-ui
--------
valence-ui provides a GUI interface to invoke Valence APIs.

==========
Features
==========
Please refer the Valence blueprints for supported and in-the-pipeline features.
``https://blueprints.launchpad.net/openstack-valence``
