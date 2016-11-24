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


from valence.api import base
from valence.api import types


class ValenceError(Exception, base.APIBase):
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


class ValenceConfirmation(base.APIBase):
    """Valence Confirmation Message representation.

       Whenever confirmation response needs to send back to client
       for successfull operation

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

    def __init__(self, responsejson, status_code=400):
        Exception.__init__(self)
        data = responsejson['error']
        self.request_id = "00000000-0000-0000-0000-000000000000"
        self.code = data['code']
        self.status = status_code
        self.title = data['message']
        message_detail = " ".join(
                         [i['Message']
                          for i in data['@Message.ExtendedInfo']])
        self.detail = message_detail


class NotFound(Exception):
    status = 404


def error(requestid, error_code, http_status,
          error_title, error_detail):
    # responseobj - the response object of Requests framework
    err_obj = ValenceError()
    err_obj.request_id = "00000000-0000-0000-0000-000000000000"
    err_obj.code = error_code
    err_obj.status = http_status
    err_obj.title = error_title
    err_obj.detail = error_detail
    return err_obj.as_dict()


def httpexception(e):
    return error("", type(e).__name__, e.code, type(e).__name__, str(e))


def generalexception(e, errorcode):
    return error("", type(e).__name__, errorcode, type(e).__name__, str(e))


def confirmation(requestid, confirm_code, confirm_detail):
    # responseobj - the response object of Requests framework
    confirm_obj = ValenceConfirmation()
    confirm_obj.request_id = "00000000-0000-0000-0000-000000000000"
    confirm_obj.code = confirm_code
    confirm_obj.detail = confirm_detail
    return confirm_obj.as_dict()
