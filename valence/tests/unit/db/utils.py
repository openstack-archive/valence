# copyright (c) 2016 Intel, Inc.
#
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

import json

import etcd


def get_etcd_read_result(key, value):
    """Return EtcdResult object for read regular key"""
    data = {
        u'action': u'get',
        u'node': {
            u'modifiedIndex': 190,
            u'key': key,
            u'value': value
        }
    }
    return etcd.EtcdResult(**data)


def get_etcd_read_dir_result(dir_key, nodes):
    """Return EtcdResult object for read dir"""
    children_nodes = [{
        u'createdIndex': 37,
        u'modifiedIndex': 37,
        u'value': i.value,
        u'key': i.key} for i in nodes]

    data = {
        u'action': u'get',
        u'node': {
            u'modifiedIndex': 190,
            u'key': dir_key,
            u'value': None,
            u'dir': True,
            u'nodes': json.dumps(children_nodes)
        }
    }
    return etcd.EtcdResult(**data)


def get_etcd_write_result(key, value):
    """Return EtcdResult object for write regular key"""
    data = {
        u'action': u'set',
        u'node': {
            u'expiration': u'2013-09-14T00:56:59.316195568+02:00',
            u'modifiedIndex': 183,
            u'key': key,
            u'ttl': 19,
            u'value': value
        }
    }
    return etcd.EtcdResult(**data)


def get_test_image(**kwargs):
    return {
        'uuid': kwargs.get('uuid', 'ea8e2a25-2901-438d-8157-de7ffd68d051'),
        'name': kwargs.get('name', 'fake_name'),
        'url': kwargs.get('url', 'fake_url'),
        'auth': kwargs.get('auth', 'fake_auth'),
        'status': kwargs.get('size', 'fake_status'),
        'description': kwargs.get('description', 'fake_description'),
        'location': kwargs.get('location', 'fake_location'),
        'redfish_link': kwargs.get('redfish_link', 'fake_redfish_link'),
        'bookmark_link': kwargs.get('bookmark_link', 'fake_bookmark_link'),
        'created_at': kwargs.get('created_at', '2017-01-01 00:0:00'),
        'updated_at': kwargs.get('updated_at', '2017-01-01 00:0:00'),
    }
