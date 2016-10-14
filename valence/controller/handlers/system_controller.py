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
from oslo_log import log as logging
from valence.common import osinterface as osapi
from valence.common.redfish import api as rfsapi
import requests

LOG = logging.getLogger(__name__)


class Handler(object):
    """Valence ComputerSystem RPC handler.

    These are the backend operations. They are executed by the backend service.
    API calls via AMQP (within the ReST API) trigger the handlers to be called.

    """

    def __init__(self):
        super(Handler, self).__init__()

    def list_systems(self, context, filters):
        LOG.info(str(filters))
        return rfsapi.systems_list(None, filters)

    def get_systembyid(self, context, systemid):
        return rfsapi.get_systembyid(systemid)
