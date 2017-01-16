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

import logging

import six

LOG = logging.getLogger(__name__)


class Text(object):
    type_name = 'Text'

    @classmethod
    def validate(cls, value):
        if value is None:
            return None

        if not isinstance(value, six.string_types):
            raise ValueError("An invalid value was provided")

        return value


class String(object):
    type_name = 'String'

    @classmethod
    def validate(cls, value, min_length=0, max_length=None):
        if value is None:
            return None
        try:
            strlen = len(value)
            if strlen < min_length:
                raise ValueError('String length is less than ' + min_length)
            if max_length and strlen > max_length:
                raise ValueError('String length is greater than ' + max_length)
        except TypeError:
            raise ValueError("An invalid value was provided")

        return value


class Integer(object):
    type_name = 'Integer'

    @classmethod
    def validate(cls, value, minimum=None):
        if value is None:
            return None

        if not isinstance(value, six.integer_types):
            try:
                value = int(value)
            except Exception:
                raise ValueError("Failed to convert value to int")

        if minimum is not None and value < minimum:
            message = ("Integer '%(value)s' is smaller than"
                       " '%(min)d'.") % {'value': value, 'min': minimum}
            raise ValueError(message)

        return value


class Bool(object):
    type_name = 'Bool'

    @classmethod
    def validate(cls, value, default=None):
        if value is None:
            value = default

        if not isinstance(value, bool):
            try:
                value = value.lower() in ("yes", "true", "t", "1")
            except Exception:
                raise ValueError("Failed to convert value to bool")

        return value


class Custom(object):
    def __init__(self, user_class):
        super(Custom, self).__init__()
        self.user_class = user_class
        self.type_name = self.user_class.__name__

    def validate(self, value):
        if value is None:
            return None

        if not isinstance(value, self.user_class):
            try:
                value = self.user_class(**value)
            except Exception:
                raise ValueError("Failed to validate received value")

        return value


class List(object):
    def __init__(self, type):
        super(List, self).__init__()
        self.type = type
        self.type_name = 'List(%s)' % self.type.type_name

    def validate(self, value):
        if value is None:
            return None

        if not isinstance(value, list):
            raise ValueError("Failed to validate received value")

        try:
            return [self.type.validate(v) for v in value]
        except Exception:
            raise ValueError("Failed to validate received value")


class Dict(object):
    type_name = 'Dict'

    @classmethod
    def validate(cls, value, default={}):
        if value is None:
            value = default

        if not isinstance(value, dict):
            raise ValueError("Failed to validate received value")

        return value
