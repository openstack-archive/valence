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

.. _add-new-api:

=================================
Add a new API endpoint in Valence
=================================

In this Guide, you will find information on how to add new API in to Valence.
This guide assumes that Valence environment is already setup (if not please go
through the `readme.rst`).


Interacting with Valence
------------------------

Before starting modification/adding a new functionality in Valence, it is suggested
to check that the valence has been setup properly. This could be done by making some
REST calls to the existing APIs and verifying their response.

.. NOTE::

         curl or some other GUI REST clients(like Postman plugin for Chrome browser)
         could be used for making the REST calls.

        .. code-block:: bash

           $ curl http://localhost:8181/v1

The above REST API call will return a json with valence version specific details. This
ensure that Valence has been setup rightly.


Example 'Hello World' API implementation
----------------------------------------

Consider we want to implement a new API /v1/example that returns "hello world" json.

#. Create a python module inside api/v1 directory that
   handles the API call

        .. code-block:: python

           #valence/api/v1/example.py

           from flask import request
           from flask_restful import Resource
           import logging

           LOG = logging.getLogger(__name__)

           class Example(Resource):
               def get(self):
               LOG.debug("GET /example")
               return {“msg” : “hello world”}

      .. note:: Check the valence/common/utils.py for commonly used functions
                and valence/common/exceptions.py for valence structured
                errors and standard confirmation messages.

#. Add a new route at 'routes.py' to receive requests at particular URL extension

        .. code-block:: python

           from valence.api.v1.example import Example
           ...
           ...
           api.add_resource(Example, '/v1/example',
                                       endpoint='example')

#. Start/Restart the valence server

        .. code-block:: bash

           $ python -m valence.cmd.api

        .. note:: Ensure config(/etc/valence/valence.conf) and
                  log(/var/log/valence/valence.log) files exists.


#. Test the service manually by issuing a GET request to /v1/example

        .. code-block:: bash

           $ curl http://localhost:8181/v1/example


#. Run tox testing to check pep8 and python2.7 compatibility. This
   should be ran from the valence root directory(where tox.ini is
   present)

        .. code-block:: bash

           $ tox -e pep8,py27


#. Update the automated testing scripts to include the new API.
        .. include:: add_new_functional_testing.rst

