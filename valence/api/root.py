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

from flask import abort
from flask import request
from flask import Response
from flask_restful import Resource

from valence.api import base
from valence.api import link
from valence.api import types
from valence.common import utils
from valence.redfish import redfish as rfs


class Version(base.APIBase):
    """An API version representation."""

    fields = {
        'id': {
            'validate': types.Text.validate
        },
        'links': {
            'validate': types.List(types.Custom(link.Link)).validate
        },
        'min_version': {
            'validate': types.Text.validate
        },
        'max_version': {
            'validate': types.Text.validate
        },
        'status': {
            'validate': types.Text.validate
        },
    }

    @staticmethod
    def convert(id, min_version, current=False):
        version = Version()
        version.id = id
        version.status = "CURRENT" if current else "DEPRECTED"
        version.min_version = min_version
        version.links = [link.Link.make_link('self', request.url_root,
                                             id, '', bookmark=True)]
        return version


class RootBase(base.APIBase):

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
        'name': {
            'validate': types.Text.validate
        },
    }

    @staticmethod
    def convert():
        root = RootBase()
        root.name = "OpenStack Valence API"
        root.description = "Valence is an OpenStack project"
        root.versions = [Version.convert('v1', '', True)]
        return root


class Root(Resource):

    def get(self):
        obj = RootBase.convert()
        return utils.make_response(
            200,
            json.loads(json.dumps(obj, default=lambda o: o.as_dict())))


class PODMProxy(Resource):
    """Passthrough Proxy for PODM.

    This function bypasses valence processing
    and calls PODM directly. This function may be temporary

    """
    @staticmethod
    def check_url(url):
        # The url will be routed to PODMProxy resource if it didn't match
        # others. So filter out these incorrect url.
        # Only support proxy request of below podm API
        resource = url.split("/")[0]
        filterext = ["Chassis", "Services", "Managers", "Systems",
                     "EventService", "Nodes", "EthernetSwitches"]
        if resource not in filterext:
            abort(404)

    def get(self, url):
        self.check_url(url)
        resp = rfs.send_request(url)
        return Response(resp.text, resp.status_code, resp.headers.items())

    def post(self, url):
        self.check_url(url)
        resp = rfs.send_request(url,
                                "POST",
                                headers={'Content-type': 'application/json'},
                                data=request.data)
        return Response(resp.text, resp.status_code, resp.headers.items())

    def delete(self, url):
        self.check_url(url)
        resp = rfs.send_request(url, "DELETE")
        return Response(resp.text, resp.status_code, resp.headers.items())

    def patch(self, url):
        self.check_url(url)
        resp = rfs.send_request(url,
                                "PATCH",
                                headers={'Content-type': 'application/json'},
                                data=request.data)
        return Response(resp.text, resp.status_code, resp.headers.items())
