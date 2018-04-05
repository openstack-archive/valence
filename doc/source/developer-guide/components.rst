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

.. _valence-components:

==========
Components
==========

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
valence-ui makes us of React.js javascript library and invoke Valence REST APIs through ajax REST calls.
