# Copyright 2017 Intel.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from valence.common import clients
from valence.common import exception

LOG = logging.getLogger(__name__)


def create_ironicclient():
    """Creates ironic client object.

        :returns: Ironic client object
    """
    try:
        osc = clients.OpenStackClients()
        return osc.ironic()
    except Exception:
        message = ('Error occurred while communicating to Ironic')
        LOG.exception(message)
        raise exception.ValenceException(message)
