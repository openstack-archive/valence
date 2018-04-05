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

.. _valence_add_new_developer_guide:

============================
Add a developer guide doc
============================

Adding a new developer guide document generally takes three steps:

1. Write an rst file for doc
----------------------------

Write a new rst file for developer guide document,
which should be placed correspondingly in valence/doc/source.

2. Check TOC tree for docs
--------------------------

We should check TOC tree ref for your newly added rst file,
ensure that your rst file can be generated according to valence/doc/source/index.rst.

3. Generate docs
----------------

Regenerate all the docs including your newly added rst file:
        .. code-block:: bash

           $ tox -e docs

Or, directly run sphinx in valence/doc:
        .. code-block:: bash

           $ python setup.py build_sphinx
