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


class APIBase(object):

    def __init__(self, **kwargs):
        for field in self.fields:
            if field in kwargs:
                value = kwargs[field]
                setattr(self, field, value)

    def __setattr__(self, field, value):
        if field in self.fields:
            validator = self.fields[field]['validate']
            value = validator(value)
            super(APIBase, self).__setattr__(field, value)

    def as_dict(self):
        """Render this object as a dict of its fields."""
        return {f: getattr(self, f)
                for f in self.fields
                if hasattr(self, f)}

    def __json__(self):
        return self.as_dict()
