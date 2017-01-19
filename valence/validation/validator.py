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

import logging

from functools import wraps
import jsonschema
from jsonschema import validators

from valence.validation import schemas

LOG = logging.getLogger(__name__)


def check_input(validator, request):
    def decorated(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            data = request.json
            LOG.debug("validating input %s with %s", data, validator.name)
            validator.validate(data)
            return f()
        return wrapper
    return decorated


class Validator(object):
    def __init__(self, name):
        self.name = name
        self.schema = schemas.SCHEMAS.get(name)
        checker = jsonschema.FormatChecker()
        self.validator = validators.Draft4Validator(self.schema,
                                                    format_checker=checker)

    def validate(self, data):
        try:
            self.validator.validate(data)
        except jsonschema.ValidationError as ex:
            LOG.exception(ex.message)
            # TODO(ramineni):raise valence specific exception
            raise Exception(ex.message)
