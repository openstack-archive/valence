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

from pecan import expose
from pecan import request
from pecan import route
from valence.api.controllers import base
from valence.api.controllers import link
from valence.api.controllers import types
from valence.common.redfish import api as rfsapi

class MediaType(base.APIBase):
    """A media type representation."""

    fields = {
        'base': {
            'validate': types.Text.validate
        },
        'type': {
            'validate': types.Text.validate
        },
    }


class V1(base.APIBase):
    """The representation of the version 1 of the API."""

    fields = {
        'id': {
            'validate': types.Text.validate
        },
        'media_types': {
            'validate': types.List(types.Custom(MediaType)).validate
        },
        'links': {
            'validate': types.List(types.Custom(link.Link)).validate
        },
        'services': {
            'validate': types.List(types.Custom(link.Link)).validate
        },
    }

    @staticmethod
    def convert():
        v1 = V1()
        v1.id = "v1"
        v1.links = [link.Link.make_link('self', request.host_url,
                                        'v1', '', bookmark=True),
                    link.Link.make_link('describedby',
                                        'http://docs.openstack.org',
                                        'developer/valence/dev',
                                        'api-spec-v1.html',
                                        bookmark=True, type='text/html')]
        v1.media_types = [MediaType(base='application/json',
                          type='application/vnd.openstack.valence.v1+json')]
        v1.services = [link.Link.make_link('self', request.host_url,
                                           'services', ''),
                       link.Link.make_link('bookmark',
                                           request.host_url,
                                           'services', '',
                                           bookmark=True)]
        return v1


class V1Controller(object):
    @expose('json')
    def index(self):
        return V1.convert()

    @expose('json')
    def _default(self, *args):
        """ this function just acts as a passthrough proxy
         This is a temperory function and will be removed subsequently
        """
        ext = args[0]
        filterext = ["Chassis","Services","Managers","Systems",
                     "EventService","Nodes","EthernetSwitches"]
        if ext in filterext:
            urlext = '/'.join(args)
            resp = rfsapi.send_request(urlext)
            return resp.json()
        else:
            abort(404)

