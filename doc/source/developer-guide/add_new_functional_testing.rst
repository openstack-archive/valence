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

.. _valence_functional_testcase:

==========================
Add a Functional Test case
==========================

Getting used to writing testing code and running this code in parallel is considered
as a good workflow.
Whenever an API for valence is implemented, it is necessary to include
the corresponding test case in the testing framework.
Currently, valence uses pythons unittest module for running the test cases.

Tests scripts are located in `<valence_root>/valence/tests
<https://github.com/openstack/valence>`_ directory

.. NOTE::
      valence/tests/__init__.py contains the base class for FunctionalTest


Implementing a Test Case
------------------------

Consider implementing an functional testcase for our /example(:ref:`add-new-api`) API


The characteristics of /example(:ref:`add-new-api`) API

* REST Method : GET
* Parameters  : Nil
* Expected Response Status : 200
* Expected Response JSON   : {“msg” : “hello world”}

To implement a testcase for the /example api,

Create a class in valence/tests/functional/test_functional.py
which inherits the FunctionalTest class from valence/tests/__init__.py
i.e.

  .. code-block:: python

    # valence/tests/functional/test_functional.py

    class TestExampleController(FunctionalTest):

        def test_example_get(self):
            response = self.app.get('/example')
            #Call GET method of /example from Flask APP
            #If REST call went fine, we expect HTTP STATUS 200 along with JSON
            assert response.status_code == 200
            #Test the status
            assert response["msg"] == "hello world"
            #Test the response message
            #likely we could test headers for content-type..etc

        def test_example_post(self):
            #suppose consider if POST is implemented & returns STATUS 201
            response = self.app.post('/example')
            assert response.status_code == 201

The above is a very basic example which could be extended to test complex JSONs
and response headers.

Also for every new code added, it is better to do pep8 and other python automated
syntax checks. As we have tox integrated in to valence, this could be achieved by,
running the below command from the valence root directory(where tox.ini is present)

        .. code-block:: bash

           $ tox -e pep8,py27

