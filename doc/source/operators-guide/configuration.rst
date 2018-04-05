..
      Copyright (c) 2018 NEC, Corp.
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

Valence provides configuration file to configure Valence service specific to
your requirements.
This file is typically located at ``/etc/valence/valence.conf``.

The configuration file is organized into the following sections:

* ``[DEFAULT]`` - General configuration
* ``[api]`` - API server configuration
* ``[etcd]`` - etcd configurations
* ``[ironic_client]`` - Options for ironic client
* ``[podm]`` - Configuration options for podm service

You can easily generate and update a sample configuration file
named `valence.conf.sample` by using following commands::

    $ git clone https://github.com/openstack/valence.git
    $ cd valence/
    $ tox -e genconfig
    $ vi etc/valence.conf.sample

Some configuration options are mentioned here, it is recommended that you
review all the options so that the valence service is configured for your needs.

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

#. Configure the details of the etcd via ``port`` and ``host`` option.
   In the following, replace PORT_NUMBER with the port of etcd service,
   and replace HOST_IP with the IP address where the etcd service is running::

    [etcd]

    # The port for the etcd server. (port value)
    port=PORT_NUMBER

    # The listen IP for the etcd server. (IP address value)
    host=HOST_IP

#. Valence shall communicate with the ironic client in order to create node in
   Ironic, which requires the Valence service to be configured with the right
   credentials for the ironic client service.
   In the configuration section here below:

   * replace IDENTITY_IP with the IP of the Identity server
   * replace IRONIC_PASSWORD with the password you chose for the ``ironic``
     user
   * replace PROJECT_NAME with the name of project created for
     OpenStack services (e.g. ``service``) ::

       [ironic_client]

       # The name of user to interact with Ironic API service. (string value)
       username = ironic

       # Password of the user specified to authorize to communicate with the
       # Ironic API service. (string value)
       password = IRONIC_PASSWORD

       # The project name which the user belongs to. (string value)
       project = PROJECT_NAME

       # The OpenStack Identity Service endpoint to authorize the user
       # against. (string value)
       auth_url = http://<IDENTITY_IP>/identity

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
