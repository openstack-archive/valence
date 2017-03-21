#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sys

from oslo_log import log as logging
import stevedore

LOG = logging.getLogger(__name__)


def load_driver(driver='ironic'):
    """Load an orchestration driver module.

    Load the orchestration driver module specified by the driver
    configuration option or, if supplied, the driver name supplied as an
    argument.
    :param driver: orchestration driver name to override config opt
    :returns: a OrchestrationDriver instance
    """
    if not driver:
        LOG.error("Orchestration driver option required, "
                  "but not specified")
        sys.exit(1)

    LOG.info("Loading orchestration driver '%s'" % driver)
    try:
        driver = stevedore.driver.DriverManager(
            "valence.driver.driver",
            driver,
            invoke_on_load=True).driver

        if not isinstance(driver, OrchestrationDriver):
            raise Exception('Expected driver of type: %s' %
                            str(OrchestrationDriver))

        return driver
    except Exception:
        LOG.exception("Unable to load the orchestration driver")
        sys.exit(1)


def node_register(node):
    driver = load_driver()
    return driver.node_register(node)


class OrchestrationDriver(object):
    '''Base class for orchestration driver.

    '''

    def register(self, node_uuid):
        """Register a node."""
        raise NotImplementedError()
