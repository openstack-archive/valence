# Copyright 2017 Intel.
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

import abc
import logging

import stevedore

from valence.common import exception

LOG = logging.getLogger(__name__)


def load_driver(driver='ironic'):
    """Load an provisioning driver module.

    Load the provisioning driver module specified by the driver
    configuration option or, if supplied, the driver name supplied as an
    argument.
    :param driver: provisioning driver name to override config opt
    :returns: a ProvisioningDriver instance
    """
    LOG.info("Loading provisioning driver '%s'" % driver)
    try:
        driver = stevedore.driver.DriverManager(
            "valence.provision.driver",
            driver,
            invoke_on_load=True).driver

        if not isinstance(driver, ProvisioningDriver):
            raise Exception('Expected driver of type: %s' %
                            str(ProvisioningDriver))

        return driver
    except Exception:
        LOG.exception("Unable to load the provisioning driver")
        raise exception.ValenceException("Failed to load %s driver" % driver)


def node_register(node, param):
    driver = load_driver()
    return driver.node_register(node, param)


class ProvisioningDriver(object):
    '''Base class for provisioning driver.

    '''

    @abc.abstractmethod
    def register(self, node_uuid, param=None):
        """Register a node."""
        raise NotImplementedError()

    @abc.abstractmethod
    def deregister(self, node_uuid):
        """Unregister a node."""
        raise NotImplementedError()
