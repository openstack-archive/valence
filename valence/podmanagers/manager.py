import stevedore

from valence.db import api as db_api
from valence.common import utils

# cache podmanager connections
podm_connections = {}
# cache podm instances based on driver, to avoid loading everytime 
podm_modules = {}


def get_podm_connection(podm_id=None):
    podm_connection = podm_connections.get(podm_id, None)
    if podm_connection:
        return podm_connection
    podm_db = db_api.Connection.get_podmanager_by_uuid(podm_id).as_dict()
    (username, password) = utils.get_basic_auth_details_from_authentication(
                podm_db['authentication'])
    podm_connection = Manager(podm_db['url'], username, password,
                              podm_db['driver'])
    podm_connections[podm_id] = podm_connection
    return podm_connection


class Manager(object):

    def __init__(self, url, username, password, driver='redfishv1'):
        self.podm = self.get_podm_instance(driver, url, username, password)

    @classmethod
    def load_podm(cls, driver):
        # check if module is already loaded
        podm = podm_modules.get(driver, None)
        if not podm:
            podm = stevedore.driver.DriverManager(
                        'valence.podmanager.driver',
                        driver, invoke_on_load=False).driver
            podm_modules[driver] = podm
        return podm

    def get_podm_instance(self, driver, url, username, password):
        podm = self.load_podm(driver)
        return podm(username, password, url)
