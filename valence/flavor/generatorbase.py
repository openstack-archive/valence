# Copyright (c) 2016 Intel, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json
import uuid


class generatorbase(object):
    def __init__(self, nodes):
        self.nodes = nodes
        self.prepend_name = 'irsd-'

    def description(self):
        return "Description of plugins"

    def _flavor_template(self, name, ram, cpus, disk, extraspecs):
        return json.dumps([{"flavor":
                           {"name": name,
                            "ram": int(ram),
                            "vcpus": int(cpus),
                            "disk": int(disk),
                            "id": str(uuid.uuid4())}},
                           {"extra_specs": extraspecs}])

    def generate(self):
        raise NotImplementedError()
