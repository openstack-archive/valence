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
from valence.api.controllers.v1 import controller as v1controller


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

route(RootController, 'v1', v1controller.V1Controller())
