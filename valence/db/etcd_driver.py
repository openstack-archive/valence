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

"""etcd storage backend."""

import json
import logging

import etcd
from oslo_utils import uuidutils
import six

from valence.common import singleton
from valence import config
from valence.db import models


LOG = logging.getLogger(__name__)


def get_driver():
    return EtcdDriver(config.etcd_host, config.etcd_port)


def translate_to_models(etcd_resp, model_type):
    """Translate value in etcd response to models."""
    data = json.loads(etcd_resp.value)
    if model_type == models.PodManager.path:
        ret = models.PodManager(**data)
    elif model_type == models.Flavor.path:
        ret = models.Flavor(**data)
    else:
        # TODO(lin.a.yang): after exception module got merged, raise
        # valence specific InvalidParameter exception here
        raise Exception(
            'The model_type value: {0} is invalid.'.format(model_type))
    return ret


@six.add_metaclass(singleton.Singleton)
class EtcdDriver(object):
    """etcd Driver."""

    def __init__(self, host=config.etcd_host, port=config.etcd_port):
        self.client = etcd.Client(host=host, port=port)

    def create_podmanager(self, values):
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        podmanager = models.PodManager(**values)
        podmanager.save()

        return podmanager

    def get_podmanager_by_uuid(self, podmanager_uuid):
        try:
            resp = self.client.read(models.PodManager.etcd_path(
                podmanager_uuid))
        except etcd.EtcdKeyNotFound:
            # TODO(lin.a.yang): after exception module got merged, raise
            # valence specific DBNotFound exception here
            raise Exception(
                'Pod manager not found {0} in database.'.format(
                    podmanager_uuid))

        return translate_to_models(resp, models.PodManager.path)

    def delete_podmanager(self, podmanager_uuid):
        podmanager = self.get_podmanager_by_uuid(podmanager_uuid)
        podmanager.delete()

    def update_podmanager(self, podmanager_uuid, values):
        podmanager = self.get_podmanager_by_uuid(podmanager_uuid)
        podmanager.update(values)

        return podmanager

    def list_podmanager(self):
        # TODO(lin.a.yang): support filter for listing podmanager

        try:
            resp = getattr(self.client.read(models.PodManager.path),
                           'children', None)
        except etcd.EtcdKeyNotFound:
            LOG.error("Path '/pod_managers' does not exist, seems etcd server "
                      "was not initialized appropriately.")
            raise

        podmanagers = []
        for podm in resp:
            if podm.value is not None:
                podmanagers.append(translate_to_models(
                    podm, models.PodManager.path))

        return podmanagers

    def get_flavor_by_uuid(self, flavor_uuid):
        try:
            resp = self.client.read(models.Flavor.etcd_path(flavor_uuid))
        except etcd.EtcdKeyNotFound:
            # TODO(ntpttr): Change this to a valence specific exception
            # when the exceptions module is merged.
            raise Exception('Flavor {0} not found.'.format(flavor_uuid))

        return translate_to_models(resp, models.Flavor.path)

    def create_flavor(self, values):
        values['uuid'] = uuidutils.generate_uuid()

        flavor = models.Flavor(**values)
        flavor.save()

        return flavor

    def delete_flavor(self, flavor_uuid):
        flavor = self.get_flavor_by_uuid(flavor_uuid)
        flavor.delete()

    def update_flavor(self, flavor_uuid, values):
        flavor = self.get_flavor_by_uuid(flavor_uuid)
        flavor.update(values)

        return flavor

    def list_flavors(self):
        try:
            resp = getattr(self.client.read(models.Flavor.path),
                           'children', None)
        except etcd.EtcdKeyNotFound:
            LOG.error("Path '/flavors' does not exist, the etcd server may "
                      "not have been initialized appropriately.")
            raise

        flavors = []
        for flavor in resp:
            if flavor.value is not None:
                flavors.append(translate_to_models(
                    flavor, models.Flavor.path))

        return flavors
