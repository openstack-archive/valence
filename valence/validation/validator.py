import jsonschema
from jsonschema import validators
from functools import wraps
import logging

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

