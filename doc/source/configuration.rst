..
      Copyright (c) 2017 NEC, Corp.
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

.. _valence-conf:

=============================
Valence Configuration Options
=============================

The configuration file is organized into the following sections:

* ``[DEFAULT]`` - General configuration
* ``[api]`` - API server configuration
* ``[etcd]`` - etcd configurations
* ``[ironic_client]`` - Options for ironic client
* ``[podm]`` - Configuration options for podm service

#. General configuration of valence service as follow under ``DEFAULT``
   section::

    [DEFAULT]

    #log_file = /var/log/valence/valence.log
    log_level=debug
    #log_format = %(asctime)s %(name)-4s %(levelname)-4s %(message)s

#. The API server configuration values can be set as in following sample
   values::

    [api]

    bind_port=8181
    bind_host=0.0.0.0
    #enable_ssl_api = false
    workers=4
    timeout=1000
    #max_limit = 1000
    #api_paste_config = api-paste.ini
    debug=true
    #log_file = /var/log/valence/valence-api.log
    log_level=debug

#. The Valence Service stores information about its entities in a database.
   Valence uses the ETCD to store data. To configure etcd set port and host
   address as follows::

    [etcd]

    port=2379
    host=localhost

#. Configure the valence service to interact with ironic client. Change
   values accordingly in following sample values::

    [ironic_client]

    #username = <None>
    #password = <None>

    #project = <None>
    #auth_url = <None>
    #user_domain_id = <None>
    #project_domain_id = <None>
    #api_version = 1
    #os_cacert = <None>
    #os_cert = <None>
    #os_key = <None>
    #insecure = false

#. Options for podmanager services can be set as in following sample::

    [podm]

    #url = <None>
    #username = <None>
    #password = <None>
    #verify_ca = <None>
    #base_ext = /redfish/v1/

    #enable_periodic_sync = false
    #sync_interval = 30

   .. NOTE::

        To enable background synchronization of devices follow simple steps:
            * Set 'enable_periodic_sync' in /etc/valence/valence.conf to true
            * Set 'sync_interval' to interval value in seconds
            * Restart service
