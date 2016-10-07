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
import pecan
from pecan import expose
from pecan import request
from valence.controller import api as controller_api

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class StoragesController(object):

    def __init__(self, *args, **kwargs):
        super(StoragesController, self).__init__(*args, **kwargs)

    # HTTP GET /storages/
    @expose(generic=True, template='json')
    def index(self):
        LOG.debug("GET /storages")
        rpcapi = controller_api.API(context=request.context)
        LOG.debug(rpcapi)
        pecan.abort(501, "GET /storages is Not yet implemented")

    @expose(template='json')
    def get(self, storageid):
        LOG.debug("GET /storages" + storageid)
        rpcapi = controller_api.API(context=request.context)
        LOG.debug(rpcapi)
        pecan.abort(501, "GET /storages/storage is Not yet implemented")
