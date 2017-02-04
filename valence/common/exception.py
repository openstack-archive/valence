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


class RedfishException(ValenceError):

    def __init__(self, responsejson, request_id=FAKE_REQUEST_ID,
                 status_code=http_client.BAD_REQUEST):
        Exception.__init__(self)
        self.request_id = request_id
        self.status = status_code
        data = responsejson['error']
        self.code = data['code']
        self.title = data['message']
        message_detail = " ".join(
                         [i['Message']
                          for i in data['@Message.ExtendedInfo']])
        self.detail = message_detail


class ResourceExists(ValenceError):
    def __init__(self, detail='resource already exists', request_id=None):
        self.request_id = request_id
        self.status_code = http_client.METHOD_NOT_ALLOWED
        self.code = http_client.METHOD_NOT_ALLOWED
        self.title = "resource already exists"
        self.detail = detail


class NotFound(ValenceError):

    def __init__(self, detail='resource not found',
                 request_id=FAKE_REQUEST_ID):
        self.request_id = request_id
        self.status = http_client.NOT_FOUND
        self.code = "NotFound"
        self.title = "Resource NOT Found"
        self.detail = detail


class BadRequest(ValenceError):

    def __init__(self, detail='bad request', request_id=FAKE_REQUEST_ID):
        self.request_id = request_id
        self.status = http_client.BAD_REQUEST
        self.code = "BadRequest"
        self.title = "Malformed or Missing Payload in Request"
        self.detail = detail


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
