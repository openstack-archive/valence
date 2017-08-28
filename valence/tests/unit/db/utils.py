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


def get_etcd_read_result_list(path, req):
    """Return EtcdResult object for read regular key"""
    data = {
        u'action': u'get',
        u'node': {
            u'modifiedIndex': 190,
            u'key': path,
            u'dir': 'true',
            u'nodes': [
                {u'key': req[0], u'value': req[1]},
                {u'key': req[2], u'value': req[3]}]
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


def get_test_podmanager(**kwargs):
    return {
        'uuid': kwargs.get('uuid', 'ea8e2a25-2901-438d-8157-de7ffd68d051'),
        'name': kwargs.get('name', 'fake_name'),
        'url': kwargs.get('url', 'fake_url'),
        'authentication': [{
            'auth_items': {
                'password': 'fake-pass',
                'username': 'fake-admin',
            },
            'type': 'basic',
        }],
        'status': kwargs.get('size', 'fake_status'),
        'description': kwargs.get('description', 'fake_description'),
        'location': kwargs.get('location', 'fake_location'),
        'resource_uri': kwargs.get('resource_uri', 'fake_redfish_link'),
        'created_at': kwargs.get('created_at', '2016-01-01 00:00:00 UTC'),
        'updated_at': kwargs.get('updated_at', '2016-01-01 00:00:00 UTC'),
    }


def get_test_flavor(**kwargs):
    return {
        'uuid': kwargs.get('uuid', 'f0565d8c-d79b-11e6-bf26-cec0c932ce01'),
        'name': kwargs.get('name', 'fake_name'),
        'properties': {
            'memory': {
                'capacity_mib': kwargs.get('capacity_mib', 'fake_capacity'),
                'type': kwargs.get('type', 'fake_type'),
            },
            'processor': {
                'total_cores': kwargs.get('total_cores', 'fake_cores'),
                'model': kwargs.get('model', 'fake_model')
            }
        },
        'created_at': kwargs.get('created_at', '2016-01-01 00:00:00 UTC'),
        'updated_at': kwargs.get('updated_at', '2016-01-01 00:00:00 UTC'),
    }


def get_test_composed_node_db_info(**kwargs):
    return {
        'uuid': kwargs.get('uuid', 'ea8e2a25-2901-438d-8157-de7ffd68d051'),
        'name': kwargs.get('name', 'fake_name'),
        'index': kwargs.get('index', '1'),
        'resource_uri': kwargs.get(
            'resource_uri',
            '/v1/nodes/7be5bc10-dcdf-11e6-bd86-934bc6947c55/'),
        'created_at': kwargs.get('created_at', '2016-01-01 00:00:00 UTC'),
        'updated_at': kwargs.get('updated_at', '2016-01-01 00:00:00 UTC')
    }


def get_test_device_db_list(**kwargs):
    return [{
        'uuid': kwargs.get('uuid', 'ea8e2a25-2901-438d-8157-de7ffd68d051'),
        'podm_id': kwargs.get('podm_id',
                              'fa8e2a25-2901-438d-8157-de7ffd68d052'),
        'node_id': kwargs.get('node_id',
                              'ga8e2a25-2901-438d-8157-de7ffd68d053'),
        'type': kwargs.get('type', 'SSD'),
        'pooled_group_id': kwargs.get('pooled_group_id', '2001'),
        'state': kwargs.get('state', 'allocated'),
        'properties': kwargs.get(
            'properties',
            [{'disk_size': '20'},
             {'bandwidth': '100Mbps'}]),
        'extra': kwargs.get(
            'extra',
            [{'mac': '11:11:11:11:11'}]),
        'resource_uri': kwargs.get('resource_uri', '/device/11'),
        'created_at': kwargs.get('created_at', '2016-01-01 00:00:00 UTC'),
        'updated_at': kwargs.get('updated_at', '2016-01-01 00:00:00 UTC')
        },
        {
            'uuid': kwargs.get('uuid', 'ea8e2a25-2901-438d-8157-de7ffd68d044'),
            'podm_id': kwargs.get('podm_id',
                                  'fa8e2a25-2901-438d-8157-de7ffd68d045'),
            'node_id': kwargs.get('node_id',
                                  'ga8e2a25-2901-438d-8157-de7ffd68d046'),
            'type': kwargs.get('type', 'SSD'),
            'pooled_group_id': kwargs.get('pooled_group_id', '2001'),
            'state': kwargs.get('state', 'allocated'),
            'properties': kwargs.get(
                'properties',
                [{'disk_size': '10'},
                 {'bandwidth': '150Mbps'}]),
            'extra': kwargs.get(
                'extra',
                [{'mac': '11:11:11:11:11'}]),
            'resource_uri': kwargs.get('resource_uri', '/device/12'),
            'created_at': kwargs.get('created_at', '2016-01-01 00:00:00 UTC'),
            'updated_at': kwargs.get('updated_at', '2016-01-01 00:00:00 UTC')
        }]
