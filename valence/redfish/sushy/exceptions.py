# Copyright 2017 Red Hat, Inc.
# All Rights Reserved.
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


LOG = logging.getLogger(__name__)


class SushyError(Exception):
    """Basic exception for errors raised by Sushy"""

    message = None

    def __init__(self, **kwargs):
        if self.message and kwargs:
            self.message = self.message % kwargs

        super(SushyError, self).__init__(self.message)


class ConnectionError(SushyError):
    message = 'Unable to connect to %(url)s. Error: %(error)s'


class MissingAttributeError(SushyError):
    message = ('The attribute %(attribute)s is missing from the '
               'resource %(resource)s')


class MalformedAttributeError(SushyError):
    message = ('The attribute %(attribute)s is malformed in the '
               'resource %(resource)s: %(error)s')


class MissingActionError(SushyError):
    message = ('The action %(action)s is missing from the '
               'resource %(resource)s')


class InvalidParameterValueError(SushyError):
    message = ('The parameter "%(parameter)s" value "%(value)s" is invalid. '
               'Valid values are: %(valid_values)s')


class HTTPError(SushyError):
    """Basic exception for HTTP errors"""

    status_code = None
    """HTTP status code."""

    body = None
    """Error JSON body, if present."""

    code = 'Base.1.0.GeneralError'
    """Error code defined in the Redfish specification, if present."""

    detail = None
    """Error message defined in the Redfish specification, if present."""

    message = ('HTTP %(method)s %(url)s returned code %(code)s. %(error)s')

    def __init__(self, method, url, response):
        self.status_code = response.status_code
        try:
            body = response.json()
        except ValueError:
            LOG.warning('Error response from %(method)s %(url)s '
                        'with status code %(code)s has no JSON body',
                        {'method': method, 'url': url, 'code':
                         self.status_code})
            error = 'unknown error'
        else:
            # TODO(dtantsur): parse @Message.ExtendedInfo
            self.body = body.get('error', {})
            self.code = self.body.get('code', 'Base.1.0.GeneralError')
            self.detail = self.body.get('message')
            error = '%s: %s' % (self.code, self.detail or 'unknown error')

        kwargs = {'method': method, 'url': url, 'code': self.status_code,
                  'error': error}
        LOG.debug('HTTP response for %(method)s %(url)s: '
                  'status code: %(code)s, error: %(error)s', kwargs)
        super(HTTPError, self).__init__(**kwargs)


class BadRequestError(HTTPError):
    pass


class ResourceNotFoundError(HTTPError):
    # Overwrite the complex generic message with a simpler one.
    message = 'Resource %(url)s not found'


class ServerSideError(HTTPError):
    pass


class AccessError(HTTPError):
    pass


def raise_for_response(method, url, response):
    """Raise a correct error class, if needed."""
    if response.status_code < 400:
        return
    elif response.status_code == 404:
        raise ResourceNotFoundError(method, url, response)
    elif response.status_code == 400:
        raise BadRequestError(method, url, response)
    elif response.status_code in (401, 403):
        raise AccessError(method, url, response)
    elif response.status_code >= 500:
        raise ServerSideError(method, url, response)
    else:
        raise HTTPError(method, url, response)
