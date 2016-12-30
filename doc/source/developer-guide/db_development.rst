.. _valence_db_development:
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

==============
DB Development
==============

Valence uses Etcd as management DB for multi pod managers.
There is one root Etcd directory for Pod Manager, named
"/pod_managers".
Each key-value pair under directory "/pod_managers" indicates
information about one pod manager.

.. NOTE::
      All db layer codes are located in valence/db.


Add a model for db
------------------

Model definition is in file valence/db/models.py

To add a /example model for Etcd db, we should create
a class inherits the ModelBase class in valence/db/models.py
i.e.

  .. code-block:: python

    # valence/db/models.py

    class ExampleModel(ModelBase):

        # This is the Etcd dir the new model lives in
        path = "/example_model"

        # The fields will be wrapped as a value for one object
        fields = {
            'uuid': {
                'validate': types.Text.validate
            },
            'name': {
                'validate': types.Text.validate
            },

        }


Add a driver for model
----------------------

Etcd driver definition is in file valence/db/etcd_driver.py

Considering adding operations for one /example model,
to add an operation for /example model, we should create
a class in valence/db/etcd_driver.py
i.e.

  .. code-block:: python

    # valence/db/etcd_driver.py

    @six.add_metaclass(singleton.Singleton)
    class ExampleDriver(object):

        def __init__(self, host=config.etcd_host, port=config.etcd_port):
            self.client = etcd.Client(host=host, port=port)

        def get_example_object(self, object_id):
            pass

        def create_example_object(self, values):
            pass

There should be more guides to be continued later.
