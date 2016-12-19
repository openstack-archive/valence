#!/usr/bin/env python

# copyright (c) 2016 Intel, Inc.
#
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

from valence.api import types
from valence.common import base


class PodManager(base.ObjectBase):

    fields = {
        'name': {
            'validate': types.Text.validate
        },
        'url': {
            'validate': types.Text.validate
        },
        'auth': {
            'validate': types.Text.validate
        },
        'status': {
            'validate': types.Text.validate
        },
        'description': {
            'validate': types.Text.validate
        },
        'location': {
            'validate': types.Text.validate
        },
        'redfish_link': {
            'validate': types.Text.validate
        },
        'bookmark_link': {
            'validate': types.Text.validate
        },
        'created_at': {
            'validate': types.Text.validate
        },
        'updated_at': {
            'validate': types.Text.validate
        },
    }

    @staticmethod
    def convert(name=None, url=None, auth=None, status=None,
                description=None, location=None, redfish_link=None,
                bookmark_link=None, created_at=None, updated_at=None):
        pod_obj = PodManager()
        pod_obj.name = name
        pod_obj.url = url
        pod_obj.auth = auth
        pod_obj.status = status
        pod_obj.description = description
        pod_obj.location = location
        pod_obj.redfish_link = redfish_link
        pod_obj.bookmark_link = bookmark_link
        pod_obj.created_at = created_at
        pod_obj.updated_at = updated_at
        return json.dumps(pod_obj, default=lambda o: o.as_dict())
