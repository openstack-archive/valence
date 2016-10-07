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

"""
RSC base exception handling.
"""
import six

from oslo_utils import excutils


class RSCException(Exception):
    """Base RSC Exception."""

    message = "An unknown exception occurred."

    def __init__(self, **kwargs):
        try:
            super(RSCException, self).__init__(self.message % kwargs)
            self.msg = self.message % kwargs
        except Exception:
            with excutils.save_and_reraise_exception() as ctxt:
                if not self.use_fatal_exceptions():
                    ctxt.reraise = False
                    # at least get the core message out if something happened
                    super(RSCException, self).__init__(self.message)

    if six.PY2:
        def __unicode__(self):
            return unicode(self.msg)

        def use_fatal_exceptions(self):
            return False


class BadRequest(RSCException):
    message = 'Bad %(resource)s request'


class NotImplemented(RSCException):
    message = ("Not yet implemented in RSC  %(func_name)s: ")


class NotFound(RSCException):
    message = ("URL not Found")


class Conflict(RSCException):
    pass


class ServiceUnavailable(RSCException):
    message = "The service is unavailable"


class ConnectionRefused(RSCException):
    message = "Connection to the service endpoint is refused"


class TimeOut(RSCException):
    message = "Timeout when connecting to OpenStack Service"


class InternalError(RSCException):
    message = "Error when performing operation"


class InvalidInputError(RSCException):
    message = ("An invalid value was provided for %(opt_name)s: "
               "%(opt_value)s")
