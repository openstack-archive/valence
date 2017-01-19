import jsonschema
from jsonschema import validators
import logging

from valence.validation import schemas 

LOG = logging.getLogger(__name__)


class Validator(object):
    def __init__(self, name):
        self.schema = schema.SCHEMAS.get(name) 
        format_checker = jsonschema.FormatChecker()
        self.validator = validators.Draft4Validator(self.schema,
            format_checker=format_checker)

    def validate(self, vals):
        LOG.debug('Validating values: %r' % vals)
        errors = []
        try:
            self.validator.validate(vals)
        except jsonschema.ValidationError as ex:
            LOG.exception(ex.message)
            #TODO(ramineni):raise valence specific exception
            raise Exception(ex.message)
