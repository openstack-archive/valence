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

from valence.common import exception
from valence.common import singleton
import valence.conf
from valence.db import models


CONF = valence.conf.CONF

LOG = logging.getLogger(__name__)


def get_driver():
    return EtcdDriver(CONF.etcd.host, CONF.etcd.port)


def translate_to_models(etcd_resp, model_type):
    """Translate value in etcd response to models."""
    data = json.loads(etcd_resp.value)
    if model_type == models.PodManager.path:
        ret = models.PodManager(**data)
    elif model_type == models.Flavor.path:
        ret = models.Flavor(**data)
    elif model_type == models.ComposedNode.path:
        ret = models.ComposedNode(**data)
    elif model_type == models.Device.path:
        ret = models.Device(**data)
    else:
        raise exception.ValenceException("Invalid model path '%s' specified.",
                                         model_type)
    return ret


@six.add_metaclass(singleton.Singleton)
class EtcdDriver(object):
    """etcd Driver."""

    def __init__(self, host=CONF.etcd.host, port=CONF.etcd.port):
        self.client = etcd.Client(host=host, port=port)

    def create_podmanager(self, values):
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        podmanager = models.PodManager(**values)
        podmanager.save()

        return podmanager

    def get_podmanager_by_uuid(self, podm_uuid):
        try:
            resp = self.client.read(models.PodManager.etcd_path(podm_uuid))
        except etcd.EtcdKeyNotFound:
            msg = 'Pod Manager {0} not found in database.'.format(podm_uuid)
            LOG.exception(msg)
            raise exception.NotFound(msg)

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
            msg = ("Path '/pod_managers' does not exist, seems etcd server "
                   "was not initialized appropriately.")
            LOG.error(msg)
            raise exception.ServiceUnavailable(msg)

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
            msg = 'Flavor {0} not found in database.'.format(flavor_uuid)
            LOG.exception(msg)
            raise exception.NotFound(msg)

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
            msg = ("Path '/flavors' does not exist, the etcd server may "
                   "not have been initialized appropriately.")
            LOG.error(msg)
            raise exception.ServiceUnavailable(msg)

        flavors = []
        for flavor in resp:
            if flavor.value is not None:
                flavors.append(translate_to_models(
                    flavor, models.Flavor.path))

        return flavors

    def create_composed_node(self, values):
        composed_node = models.ComposedNode(**values)
        composed_node.save()

        return composed_node

    def get_composed_node_by_uuid(self, composed_node_uuid):
        try:
            resp = self.client.read(models.ComposedNode.etcd_path(
                composed_node_uuid))
        except etcd.EtcdKeyNotFound:
            msg = ("Composed node '{0}' not found in database.".format(
                   composed_node_uuid))
            LOG.exception(msg)
            raise exception.NotFound(msg)

        return translate_to_models(resp, models.ComposedNode.path)

    def delete_composed_node(self, composed_node_uuid):
        composed_node = self.get_composed_node_by_uuid(composed_node_uuid)
        composed_node.delete()

    def update_composed_node(self, composed_node_uuid, values):
        composed_node = self.get_composed_node_by_uuid(composed_node_uuid)
        composed_node.update(values)

        return composed_node

    def list_composed_nodes(self, filters={}):
        """List composed nodes from DB

        :param filters: filters to be applied on results.
            Eg: Filter results based on podm_id {'podm_id': 'xxxx'}
        :returns: List of composed nodes after filters applied if any
        """
        try:
            resp = getattr(self.client.read(models.ComposedNode.path),
                           'children', None)
        except etcd.EtcdKeyNotFound:
            msg = ("Path '/nodes' does not exist, the etcd server may "
                   "not have been initialized appropriately.")
            LOG.error(msg)
            raise exception.ServiceUnavailable(msg)

        composed_nodes = []
        for node in resp:
            if node.value is not None:
                composed_nodes.append(translate_to_models(
                    node, models.ComposedNode.path))
        if filters:
            # Filter nodes having value specified w.r.t key
            for key, value in filters.items():
                composed_nodes = [node for node in composed_nodes
                                  if node[key] == value]
        return composed_nodes

    def list_devices(self, filters={}):
        try:
            resp = getattr(self.client.read(models.Device.path),
                           'children', None)
        except etcd.EtcdKeyNotFound:
            msg = ("Path '/devices' does not exist, the etcd server may "
                   "not have been initialized appropriately.")
            LOG.error(msg)
            raise exception.ServiceUnavailable(msg)

        devices = []
        for dev in resp:
            if dev.value is not None:
                devices.append(translate_to_models(dev, models.Device.path))

        if filters:
            for key, value in filters.items():
                devices = [dev for dev in devices if dev[key] == value]
        return devices

    def get_device_by_uuid(self, device_id):
        try:
            resp = self.client.read(models.Device.etcd_path(device_id))
        except etcd.EtcdKeyNotFound:
            msg = 'Device {0} not found in database.'.format(device_id)
            LOG.exception(msg)
            raise exception.NotFound(msg)

        return translate_to_models(resp, models.Device.path)

    def delete_device(self, device_uuid):
        device = self.get_device_by_uuid(device_uuid)
        device.delete()

    def update_device(self, device_uuid, values):
        device = self.get_device_by_uuid(device_uuid)
        device.update(values)
        return device

    def add_device(self, values):
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()
        device = models.Device(**values)
        device.save()

        return device
