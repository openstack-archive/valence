# All Rights Reserved.
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


import flask

from valence.common import base
from valence.common import types


def build_url(resource, resource_args, bookmark=False, base_url=None):
    if base_url is None:
        base_url = flask.request.root_url
    base_url = base_url.rstrip("//")
    template = '%(url)s/%(res)s' if bookmark else '%(url)s/v1/%(res)s'
    template += '%(args)s' if resource_args.startswith('?') else '/%(args)s'
    return template % {'url': base_url, 'res': resource, 'args': resource_args}


class Link(base.ObjectBase):
    """A link representation."""

    fields = {
        'href': {
            'validate': types.Text.validate
        },
        'rel': {
            'validate': types.Text.validate
        },
        'type': {
            'validate': types.Text.validate
        },
    }

    @staticmethod
    def make_link(rel_name, url, resource, resource_args,
                  bookmark=False, type=None):
        href = build_url(resource, resource_args,
                         bookmark=bookmark, base_url=url)
        if type is None:
            return Link(href=href, rel=rel_name)
        else:
            return Link(href=href, rel=rel_name, type=type)
