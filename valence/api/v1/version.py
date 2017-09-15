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

from flask import request
from flask_restful import Resource
from six.moves import http_client

from valence.api import link
from valence.common import base
from valence.common import types
from valence.common import utils


class MediaType(base.ObjectBase):
    """A media type representation."""

    fields = {
        'base': {
            'validate': types.Text.validate
        },
        'type': {
            'validate': types.Text.validate
        },
    }


class V1Base(base.ObjectBase):
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
        'nodes': {
            'validate': types.List(types.Custom(link.Link)).validate
        },
        'storages': {
            'validate': types.List(types.Custom(link.Link)).validate
        },
        'flavors': {
            'validate': types.List(types.Custom(link.Link)).validate
        },
        'systems': {
            'validate': types.List(types.Custom(link.Link)).validate
        },
        'pod_managers': {
            'validate': types.List(types.Custom(link.Link)).validate
        },
    }

    @staticmethod
    def convert():
        v1 = V1Base()
        v1.id = "v1"
        v1_base_url = request.url_root.rstrip('//')
        v1.links = [link.Link.make_link('self', request.url_root,
                                        'v1', '', bookmark=True),
                    link.Link.make_link('describedby',
                                        'https://docs.openstack.org',
                                        'developer/valence/dev',
                                        'api-spec-v1.html',
                                        bookmark=True, type='text/html')]
        v1.media_types = [MediaType(base='application/json',
                          type='application/vnd.openstack.valence.v1+json')]
        v1.nodes = [link.Link.make_link('self', v1_base_url,
                                        'nodes', ''),
                    link.Link.make_link('bookmark',
                                        v1_base_url,
                                        'nodes', '',
                                        bookmark=True)]
        v1.storages = [link.Link.make_link('self', v1_base_url,
                                           'storages', ''),
                       link.Link.make_link('bookmark',
                                           v1_base_url,
                                           'storages', '',
                                           bookmark=True)]
        v1.flavors = [link.Link.make_link('self', v1_base_url,
                                          'flavors', ''),
                      link.Link.make_link('bookmark',
                                          v1_base_url,
                                          'flavors', '',
                                          bookmark=True)]
        v1.systems = [link.Link.make_link('self', v1_base_url,
                                          'systems', ''),
                      link.Link.make_link('bookmark',
                                          v1_base_url,
                                          'systems', '',
                                          bookmark=True)]
        v1.pod_managers = [link.Link.make_link('self', v1_base_url,
                                               'pod_managers', ''),
                           link.Link.make_link('bookmark', v1_base_url,
                                               'pod_managers', '',
                                               bookmark=True)]
        return v1


class V1(Resource):

    def get(self):
        vobj = V1Base.convert()
        return utils.make_response(http_client.OK, vobj.as_dict())
