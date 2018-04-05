..
      Copyright 2016 Intel Corporation
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

.. _valence-installation:

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
Valence Installation
********************

1. Install software dependencies

   ``$ sudo apt-get install git python-pip python-dev build-essential``

2. Clone the Valence code from git repo.

   ``$ git clone https://git.openstack.org/openstack/valence``

3. Execute the 'install_valence.sh' file present in the Valence root directory.
   The install script will automatically install the dependencies listed in the
   requirements.txt file.

   ``$ sudo bash install_valence.sh``

4. Check and set the values in valence.conf located at /etc/valence/valence.conf
   as required.

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

**********************
Installation using pip
**********************

At the command line::

   $ pip install valence

Or, if you have virtualenvwrapper installed::

   $ mkvirtualenv valence
   $ pip install valence

****************
GUI installation
****************
Please refer to the installation steps in the ui-README_ file.

.. _ui-README: https://github.com/openstack/valence/blob/master/ui/README.md
