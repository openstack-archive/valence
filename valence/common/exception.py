# Copyright (c) 2016 Intel, Inc.
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
import sys

from keystoneclient import exceptions as keystone_exceptions
from six.moves import http_client

from valence.common import base
from valence.common import types

# TODO(yufei): all request id is faked as all zero string now,
# need to be replaced with real request uuid in the future
FAKE_REQUEST_ID = "00000000-0000-0000-0000-000000000000"


class ValenceError(Exception, base.ObjectBase):
    """Valence Error representation.

       As per openstack Error Schema
       http://specs.openstack.org/openstack/api-wg/guidelines/errors.html

    """
    _msg_fmt = "An unknown exception occured"
    status = http_client.INTERNAL_SERVER_ERROR

    fields = {
        'request_id': {
            'validate': types.Text.validate
        },
        'code': {
            'validate': types.Text.validate
        },
        'status': {
            'validate': types.Integer.validate
        },
        'title': {
            'validate': types.Text.validate
        },
        'detail': {
            'validate': types.Text.validate
        }
    }

    def __init__(self, detail=None, status=None, title=None, code=None,
                 request_id=None):
        self.status = status or self.status
        self.title = title or self._msg_fmt
        self.code = code or http_client.responses.get(self.status)
        self.detail = detail
        self.request_id = request_id or FAKE_REQUEST_ID

    def __str__(self):
        return self.title + ':' + self.detail


class ValenceConfirmation(base.ObjectBase):
    """Valence Confirmation Message representation.

       Whenever confirmation response needs to send back to client
       for successful operation

    """

    fields = {
        'request_id': {
            'validate': types.Text.validate
        },
        'code': {
            'validate': types.Text.validate
        },
        'detail': {
            'validate': types.Text.validate
        }
    }


class ValenceException(ValenceError):
    pass


class ServiceUnavailable(ValenceError):
    status = http_client.SERVICE_UNAVAILABLE
    _msg_fmt = "Connection Error"


class RedfishException(ValenceError):

    def __init__(self, responsejson, request_id=None, status_code=None):
        data = responsejson['error']
        self.code = data['code']
        self.title = data['message']
        message_detail = " ".join([i['Message']
                                  for i in data['@Message.ExtendedInfo']])

        super(RedfishException, self).__init__(message_detail, status_code,
                                               self.title, self.code,
                                               request_id)


class ExpEtherException(ValenceError):
    _msg_fmt = "ExpEther Exception"


class ResourceExists(ValenceError):
    status = http_client.CONFLICT
    _msg_fmt = "Resource Already Exists"


class NotFound(ValenceError):
    status = http_client.NOT_FOUND
    _msg_fmt = "Resource could not be found"


class DriverNotFound(NotFound):
    _msg_fmt = "Unsupported Driver Specified"


class BadRequest(ValenceError):
    status = http_client.BAD_REQUEST
    _msg_fmt = "Bad Request"


class ValidationError(BadRequest):
    _msg_fmt = "Validation Error"


class AuthorizationFailure(ValenceError):
    status = http_client.UNAUTHORIZED
    _msg_fmt = "Authorization Error"


def _error(error_code, http_status, error_title, error_detail,
           request_id=FAKE_REQUEST_ID):
    # responseobj - the response object of Requests framework
    err_obj = ValenceError()
    err_obj.request_id = request_id
    err_obj.code = error_code
    err_obj.status = http_status
    err_obj.title = error_title
    err_obj.detail = error_detail
    return err_obj.as_dict()


def httpexception(e):
    return _error(type(e).__name__, e.code, type(e).__name__, str(e))


def generalexception(e, errorcode):
    return _error(type(e).__name__, errorcode, type(e).__name__, str(e))


def confirmation(request_id=FAKE_REQUEST_ID, confirm_code='',
                 confirm_detail=''):
    # responseobj - the response object of Requests framework
    confirm_obj = ValenceConfirmation()
    confirm_obj.request_id = request_id
    confirm_obj.code = confirm_code
    confirm_obj.detail = confirm_detail
    return confirm_obj.as_dict()


def wrap_keystone_exception(func):
    """Wrap keystone exceptions and throw Valence specific exceptions."""
    @functools.wraps(func)
    def wrapped(*args, **kw):
        try:
            return func(*args, **kw)
        except keystone_exceptions.AuthorizationFailure:
            message = ("%s connection failed. Reason: "
                       "%s" % (func.__name__, sys.exc_info()[1]))
            raise AuthorizationFailure(detail=message)
        except keystone_exceptions.ClientException:
            message = ("%s connection failed. Unexpected keystone client "
                       "error occurred: %s" % (func.__name__,
                                               sys.exc_info()[1]))
            raise AuthorizationFailure(detail=message)
    return wrapped
