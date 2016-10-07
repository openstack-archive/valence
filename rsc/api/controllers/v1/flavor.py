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

from oslo_config import cfg
from oslo_log import log as logging
from pecan import expose
from pecan import request
from rsc.controller import api as controller_api

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class FlavorController(object):

    def __init__(self, *args, **kwargs):
        super(FlavorController, self).__init__(*args, **kwargs)

    # HTTP GET /flavor/
    @expose(generic=True, template='json')
    def index(self):
        LOG.debug("GET /flavor")
        rpcapi = controller_api.API(context=request.context)
        res = rpcapi.flavor_options()
        return res

    # HTTP POST /flavor/
    @index.when(method='POST', template='json')
    def index_POST(self, **kw):
        LOG.debug("POST /flavor")
        rpcapi = controller_api.API(context=request.context)
        res = rpcapi.flavor_generate(criteria=kw['criteria'])
        return res
