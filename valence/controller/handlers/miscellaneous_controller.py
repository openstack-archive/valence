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
from valence.common.redfish import api as rfsapi

LOG = logging.getLogger(__name__)


class Handler(object):
    """Valence Miscellaneous RPC handler.

    These are the backend operations. They are executed by the backend ervice.
    API calls via AMQP (within the ReST API) trigger the handlers to be called.

    """

    def __init__(self):
        super(Handler, self).__init__()

    # POD(s) related operations
    def list_pods(self, context, filters):
        return rfsapi.list_pods(filters)

    def get_podbyid(self, context, podid):
        return rfsapi.list_pods({'Id':podid})

    # Rack(s) related operations
    def list_racks(self, context, filters):
        return rfsapi.list_racks(filters)

    def get_rackbyid(self, context, rackid):
        return rfsapi.list_racks({'Id':rackid})

