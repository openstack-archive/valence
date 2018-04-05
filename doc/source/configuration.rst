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

To generate sample valence.conf file, run the following command::

   $ sudo tox -egenconfig

This will generate sample conf file: etc/valence.conf.sample

#. General configuration of valence service as follow under ``DEFAULT``
   section::

    [DEFAULT]

    # The log file location for valence service
    log_file = /var/log/valence/valence.log

    # The granularity of log outputs. By default set to info level
    # Possible values: info, critical, warning, debug, error, notset
    log_level=debug

    # The log format
    log_format = %(asctime)s %(name)-4s %(levelname)-4s %(message)s

#. The API server configuration values can be set as in following sample
   values::

    [api]

    # The port for the valence API server. (port value)
    bind_port=8181

    # The listen IP for the valence API server. (IP address value)
    bind_host=0.0.0.0

    # Enable the integrated stand-alone API to service requests via HTTPS
    # instead of HTTP. If there is a front-end service performing HTTPS
    # offloading from the service, this option should be False; note, you
    # will want to change public API endpoint to represent SSL termination
    # URL with 'public_endpoint' option. (boolean value)
    enable_ssl_api = false

    # Number of workers for valence-api service. The default will be the
    # number of CPUs available. (integer value)
    workers=4

    # The maximum timeout to wait for valence API server to come up.
    # (integer value)
    timeout=1000

    # The maximum number of items returned in a single response from a
    # collection resource. (integer value)
    max_limit = 1000

    # Configuration file for WSGI definition of API. (string value)
    api_paste_config = api-paste.ini

    # Start API server in debug mode. (boolean value)
    debug=true

    # The log file location for valence API server (string value)
    log_file = /var/log/valence/valence-api.log

    # The granularity of API server log outputs. (string value)
    # Possible values: info, critical, warning, debug, error
    log_level=debug

#. The Valence Service stores information about its entities in a database.
   Valence uses the ETCD to store data. To configure etcd set port and host
   address as follows::

    [etcd]

    # The port for the etcd server. (port value)
    port=2379

    # The listen IP for the etcd server. (IP address value)
    host=127.0.0.1

#. Configure the valence service to interact with ironic client. Change
   values accordingly in following sample values::

    [ironic_client]

    # The name of user to interact with Ironic API service. (string value)
    username = ironic

    # Password of the user specified to authorize to communicate with the
    # Ironic API service. (string value)
    password = password

    # The project name which the user belongs to. (string value)
    project = service

    # The OpenStack Identity Service endpoint to authorize the user
    # against. (string value)
    auth_url = http://0.0.0.0/identity

    # ID of a domain the user belongs to. (string value)
    user_domain_id = default

    # ID of a domain the project belongs to. (string value)
    project_domain_id = default

    # Version of Ironic API to use in ironicclient. (string value)
    api_version = 1

    # Optional CA cert file to use in SSL connections. (string value)
    os_cacert = None

    # Optional PEM-formatted certificate chain file. (string value)
    os_cert = None

    # Optional PEM-formatted file that contains the private key. (string
    # value)
    os_key = None

    # If set, then the server's certificate will not be verified. (boolean
    # value)
    insecure = false

#. Options for podmanager services can be set as in following sample::

    [podm]
    # To enable periodic task to automatically sync resources of podmanager
    # with DB. By default it is set to false. (boolean value)
    enable_periodic_sync = false

    # Time interval(in seconds) after which devices will be synced
    # periodically. By default it is set to 30. (integer value)
    sync_interval = 30

   To enable background synchronization of devices follow simple steps:
    * Set 'enable_periodic_sync' in /etc/valence/valence.conf to true
    * Set 'sync_interval' to interval value in seconds
    * Restart service
