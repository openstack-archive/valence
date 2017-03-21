# Copyright (c) 2017 NEC, Corp.
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

import functools
import logging

from flask import request
import jsonschema

from valence.common import exception
from valence.validation import schemas

LOG = logging.getLogger(__name__)


def check_input(schema_name):
    def decorated(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            LOG.debug("validating input %s with schema %s", data, schema_name)
            schema_validator = Validator(schema_name)
            schema_validator.validate(data)
            return f(*args, **kwargs)
        return wrapper
    return decorated


class Validator(object):
    def __init__(self, name):
        self.name = name
        self.schema = schemas.SCHEMAS.get(name)
        checker = jsonschema.FormatChecker()
        self.validator = jsonschema.Draft4Validator(self.schema,
                                                    format_checker=checker)

    def validate(self, data):
        try:
            self.validator.validate(data)
        except jsonschema.ValidationError as e:
            if len(e.path) > 0:
                detail = (("Invalid input for field/attribute '%(path)s' "
                           "Value: '%(value)s'. %(message)s") %
                          {'path': e.path.pop(), 'value': e.instance,
                           'message': e.message})
            else:
                detail = e.message
            LOG.exception("Failed to validate the input")
            raise exception.ValidationError(detail=detail)
