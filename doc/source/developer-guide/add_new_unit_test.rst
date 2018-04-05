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

.. _valence_unit_testcase:

====================
Add a Unit Test case
====================

Getting used to writing testing code and running this code in parallel is considered
a good workflow.
Whenever an API for valence is implemented, it is necessary to include
the corresponding unit test case in the testing framework.
Currently, when adding a unit test, valence uses basic libraries e.g. unittest, mock.

Unit tests scripts are located in `<valence_root>/valence/tests/unit/
<https://github.com/openstack/rsc/tree/master/valence/tests/unit>`_ directory

.. NOTE::
      Place your unit test in the corresponding directory in valence/tests/unit.

      "valence/tests/unit/fakes" contains the fake data for all the units.


Implement a Unit Test Case
-----------------------------

Consider implementing a unit test case for our example unit module.

To implement a unit test case for the example unit module,

Create a class in valence/tests/unit/(directory)/test_(example).py,
which inherits the TestCase class from unittest.
i.e.

  .. code-block:: python

    # valence/tests/unit/redfish/test_redfish.py

    class TestRedfish(TestCase):

        # This should be any function name your want to test
        def test_get_rfs_url(self):
            cfg.podm_url = "https://127.0.0.1:8443"
            expected = urljoin(cfg.podm_url, "redfish/v1/Systems/1")

            # test without service_ext
            result = redfish.get_rfs_url("/Systems/1/")
            self.assertEqual(expected, result)

Also if you want to add fakes data in unit test,
please put fakes data in "valence/tests/unit/fakes",
which should be named valence/tests/unit/fakes/(example)_fakes.py.

For every bit of new code added, it is better to do pep8 and other python automated
syntax checks. As we have tox integrated in to valence, this could be achieved by
running the below command from the valence root directory(where tox.ini is present).

        .. code-block:: bash

           $ tox -e pep8,py27
