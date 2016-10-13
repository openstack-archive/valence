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
from valence.api.controllers.v1.controller import V1Controller
from valence.api.controllers.v1 import flavor as v1flavor
from valence.api.controllers.v1 import miscellaneous as v1miscellaneous
from valence.api.controllers.v1 import nodes as v1nodes
from valence.api.controllers.v1 import systems as v1systems


class Version(base.APIBase):
    """An API version representation."""

    fields = {
        'id': {
            'validate': types.Text.validate
        },
        'links': {
            'validate': types.List(types.Custom(link.Link)).validate
        },
    }

    @staticmethod
    def convert(id):
        version = Version()
        version.id = id
        version.links = [link.Link.make_link('self', request.host_url,
                                             id, '', bookmark=True)]
        return version


class Root(base.APIBase):

    fields = {
        'id': {
            'validate': types.Text.validate
        },
        'description': {
            'validate': types.Text.validate
        },
        'versions': {
            'validate': types.List(types.Custom(Version)).validate
        },
        'default_version': {
            'validate': types.Custom(Version).validate
        },
    }

    @staticmethod
    def convert():
        root = Root()
        root.name = "OpenStack Valence API"
        root.description = ("Valence is an OpenStack project")
        root.versions = [Version.convert('v1')]
        root.default_version = Version.convert('v1')
        return root


class RootController(object):
    @expose('json')
    def index(self):
        return Root.convert()


route(RootController, 'v1', V1Controller())
route(V1Controller, 'flavor', v1flavor.FlavorController())
route(V1Controller, 'nodes', v1nodes.NodesController())
route(V1Controller, 'systems', v1systems.SystemsController())
route(V1Controller, 'pods', v1miscellaneous.PodsController())
route(V1Controller, 'racks', v1miscellaneous.RacksController())
