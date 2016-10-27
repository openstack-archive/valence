# Copyright 2015 Lenovo
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
import requests
import time
from ironic.common.i18n import _
from ironic.common import exception

_logger = logging.getLogger(__name__)

"""
confluent related code, currenly, from this client,
confluent support create/update/delete/search operations
"""


def get_confluent_connection(context, ip, user, passwd):
    """
    get the confluent connection by detail info
    """
    _logger.info('get the confluent connection')
    confluent_api = ConfluentAPI(context, ip, user, passwd)
    _logger.info('end of getting the confluent connection')
    return confluent_api


def _http_log_req(method, url, body=None, headers=None):
    if not _logger.isEnabledFor(logging.DEBUG):
        return

    _logger.debug("REQ:%(method)s %(url)s %(headers)s %(body)s\n",
                  {'method': method,
                   'url': url,
                   'headers': headers,
                   'body': body})


def _http_log_resp(resp, body):
    if not _logger.isEnabledFor(logging.DEBUG):
        return

    _logger.debug("RESP:%(code)s %(headers)s %(body)s\n",
                  {'code': resp.status_code,
                   'headers': resp.headers,
                   'body': body})


class ConfluentAPI(object):
    """Client for interacting with Confluent via a REST API."""

    def __init__(self, context, host, username, password, **kwargs):
        self.context = context
        self.host = host
        self.username = username
        self.password = password

        self.scheme = kwargs.pop('scheme', 'http')
        self.retries = kwargs.pop('retries', 1)
        self.port = kwargs.pop('port', 4005)
        self.retry_interval = kwargs.pop('retry_interval', 1)
        self.verify = kwargs.pop('verify', False)

    def _do_request(self, method, url, body=None, headers=None):
        """now, the confluent is very simple, for create/delete/update, we care
        about the return code, not the response txt
        """

        url = "%s://%s:%s%s" % (self.scheme, self.host, self.port, url)

        try:
            _http_log_req(method, url, body, headers)
            resp = requests.request(method, url, data=body,
                                    headers=headers,
                                    auth=(self.username, self.password),
                                    verify=self.verify)
            _http_log_resp(resp, resp.text)

            status_code = resp.status_code
            _logger.warn('status code is %(status)s.', {'status': status_code})
            if status_code in (requests.codes.OK,
                               requests.codes.CREATED,
                               requests.codes.ACCEPTED,
                               requests.codes.NO_CONTENT):
                return status_code, resp.text
            else:
                _logger.warn('request failed...')
                return status_code, ''

        except requests.exceptions.ConnectionError as e:
            _logger.debug("throwing ConnectionFailed : %s", e)
            msg = _("request to confluent server failed")
            raise exception.InvalidParameterValue(msg)

    def _retry_request(self, method, action_url, body=None, headers=None):
        """Call do_request with the default retry configuration.
        Only idempotent requests should retry failed connection attempts.
        """
        # if headers is None:
        #    headers = {'Content-Type':'application/json'}

        max_attempts = self.retries + 1
        for i in range(max_attempts):
            try:
                return self._do_request(method, action_url, body=body,
                                        headers=headers)
            except exception.InvalidParameterValue as e:
                # Exception has already been logged by do_request()
                if i < self.retries:
                    _logger.debug('Retrying connection to Confluent server')
                    time.sleep(self.retry_interval)
                else:
                    raise e
        if self.retries:
            msg = ("Failed to connect to Confluent server after %d attempts"
                   % max_attempts)
        else:
            msg = _("Failed to connect Confluent server")

        raise exception.InvalidParameterValue(msg)

    def create_confluent_node(self, manager, name, passwd, user,
                              method='ipmi'):
        """add a node into confluent server, with manager and name, method first
        , when the user update the authentication in UI, do the update then"""

        post_body = {'console.method': method}
        if name and manager:
            post_body['name'] = name
            post_body['hardwaremanagement.manager'] = manager
            if passwd:
                post_body['secret.hardwaremanagementpassword'] = passwd
            if user:
                post_body['secret.hardwaremanagementuser'] = user

            self._retry_request('POST', '/nodes/', post_body)

    def update_confluent_node(self, manager, name, method, passwd, user):
        """update the created confluent node, if the node does not exist, create it"""

        found = self.search_confluent_node(name)
        if found:
            update_body = {}
            if manager:
                update_body['hardwaremanagement.manager'] = manager
            if method:
                update_body['console.method'] = method
            if passwd:
                update_body['secret.hardwaremanagementpassword'] = passwd
            if user:
                update_body['secret.hardwaremanagementuser'] = user

            self._retry_request('PUT', '/nodes/' + name + '/attributes/all',
                                update_body)
        else:
            self.create_confluent_node(manager, name, None, None,
                                       method="ipmi")

    def delete_confluent_node(self, name):
        """delete the confluent node"""
        self._retry_request('DELETE', '/nodes/' + name + '/')

    def search_confluent_node(self, name):
        """check if the node exist in confluent server side"""
        status, res = self._retry_request('GET', '/nodes/' + name + '/')
        if status == requests.codes.OK:
            return True
        return False
