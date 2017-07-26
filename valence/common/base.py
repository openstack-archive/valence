#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import json


class ObjectBase(object):

    def __init__(self, **kwargs):
        for field in self.fields:
            if field in kwargs:
                setattr(self, field, kwargs[field])

    def __setattr__(self, field, value):
        if field in self.fields:
            validator = self.fields[field]['validate']
            value = validator(value)
            super(ObjectBase, self).__setattr__(field, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def update(self, values):
        """Make the object behave like a dict."""
        for key, value in values.items():
            setattr(self, key, value)

    def _as_dict(self):
        """Render this object as a dict of its fields."""
        return {f: getattr(self, f)
                for f in self.fields
                if hasattr(self, f)}

    def as_dict(self):
        """Use json to make sure recurring render this object"""
        return json.loads(json.dumps(self, default=lambda o: o._as_dict()))

    def __json__(self):
        return self.as_dict()
