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

from oslo_log import log as logging
from rsc.flavor.generatorbase import generatorbase

logger = logging.getLogger()


class exampleGenerator(generatorbase):
    def __init__(self, nodes):
        generatorbase.__init__(self, nodes)

    def generate(self):
        logger.info("Example Flavor Generate")
        return {"Error": "Example Flavor Generator- Not Yet Implemented"}
