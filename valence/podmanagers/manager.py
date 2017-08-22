import logging

import stevedore

from valence.common import exception
from valence.common import utils
from valence.db import api as db_api

LOG = logging.getLogger(__name__)

# cache podmanager connections, one connection per podmanager
podm_connections = {}

# cache podmanager modules, to be loaded only once per driver
# If same driver used by 2 podmanagers (eg:redfishv1), podm_base module will be
# loaded only once, but 2 instances of class would be created.
podm_modules = {}


def get_connection(podm_id):
    podm_connection = podm_connections.get(podm_id, None)
    if podm_connection:
        return podm_connection
    podm_db = db_api.Connection.get_podmanager_by_uuid(podm_id).as_dict()
    username, password = utils.get_basic_auth_credentials(
        podm_db['authentication'])
    podm_connection = Manager(podm_db['url'], username, password,
                              podm_db['driver']).podm
    podm_connections[podm_id] = podm_connection
    return podm_connection


class Manager(object):

    def __init__(self, url, username, password, driver='redfishv1'):
        self.podm = self._get_podm_instance(driver, url, username, password)

    def _get_podm_instance(self, driver, url, username, password):
        podm = self.load_podm(driver)
        return podm(username, password, url)

    @classmethod
    def load_podm(cls, driver):
        # get module if already loaded
        podm = podm_modules.get(driver, None)
        if not podm:
            try:
                podm = stevedore.driver.DriverManager(
                    'valence.podmanager.driver',
                    driver, invoke_on_load=False).driver
            except RuntimeError:
                msg = "podmanager could not be loaded with specified driver %s"
                LOG.exception(msg % driver)
                raise exception.DriverNotFound(msg % driver)

            podm_modules[driver] = podm
        return podm
