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


from ironic.common import exception
import json
import logging
import requests



def safe_get_from_info(info, keys_content, default):
    result = info
    for key in keys_content.split('.'):
        if key in result:
            result = result[key]
        else:
            return default
    return result


class HttpMethod(object):
    def __init__(self):
        self.log = logging.getLogger(__name__)

    def do_get_request(self, url, headers=None, body=None,
                       auth=None, verify=False):
        status_code, text = self.__do_http_request("GET", url, headers,
                                                   body, auth, verify)
        try:
            return json.loads(text)
        except (TypeError, ValueError):
            self.log.error("can not parse http response text to json", text)
            return None

    def do_post_request(self, url, headers=None, body=None,
                        auth=None, verify=False):
        try:
            self.__do_http_request("POST", url, headers, body, auth, verify)
            return True
        except Exception as ex:
            self.log.error("send post http request raise Exception\n %s" % ex)
            return False

    # --------------------- helper functions -------------------- #

    def __do_http_request(self, method, url, headers=None, body=None,
                          auth=None, verify=False):
        try:
            self.__http_log_req(method, url, body, headers)
            resp = requests.request(method,
                                    url,
                                    data=body,
                                    headers=headers,
                                    auth=auth,
                                    verify=verify)
            self.__http_log_resp(resp, resp.text)
            status_code = resp.status_code
            if status_code < 300:
                return status_code, resp.text
            else:
                self.__handle_fault_response(resp)
        except requests.exceptions.ConnectionError as e:
            self.log.debug("throwing ConnectionFailed : %s", e)
            raise exception.HTTPNotFound(url=url)

    def __handle_fault_response(self, resp):
        self.log.debug("Error message: %s", resp.text)
        try:
            error_body = json.loads(resp.text)
            if error_body:
                explanation = error_body['messages'][0]['explanation']
                recovery = error_body['messages'][0]['recovery']['text']
        except Exception:
            # If unable to deserialized body it is probably not a
            explanation = resp.text
            recovery = ''
        # Raise the appropriate exception
        kwargs = {'explanation': explanation, 'recovery': recovery}
        raise exception.XClarityInternalFault(**kwargs)

    def __http_log_req(self, method, url, body=None, headers=None):
        if not self.log.isEnabledFor(logging.DEBUG):
            return
        self.log.debug("REQ:%(method)s %(url)s %(headers)s %(body)s\n",
                       {'method': method,
                        'url': url,
                        'headers': headers,
                        'body': body})

    def __http_log_resp(self, resp, body):
        if not self.log.isEnabledFor(logging.DEBUG):
            return
        self.log.debug("RESP:%(code)s %(headers)s %(body)s\n",
                       {'code': resp.status_code,
                        'headers': resp.headers,
                        'url': resp.url,
                        # 'body': body}
                        })


http = HttpMethod()
