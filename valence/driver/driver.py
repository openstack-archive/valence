#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import six
import sys

from oslo_log import log as logging
import stevedore

from valence.common import exception
from valence.common.i18n import _
from valence.common.i18n import _LE
from valence.common.i18n import _LI

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
        LOG.error(_LE("Orchestration driver option required, "
                      "but not specified"))
        sys.exit(1)

    LOG.info(_LI("Loading orchestration driver '%s'"), driver)
    try:
        driver = stevedore.driver.DriverManager(
            "valence.driver.driver",
            'ironic',
            invoke_on_load=True).driver

        if not isinstance(driver, OrchestrationDriver):
            raise Exception(_('Expected driver of type: %s') %
                            str(OrchestrationDriver))

        return driver
    except Exception:
        LOG.exception(_LE("Unable to load the orchestration driver"))
        sys.exit(1)


def node_register(node):
    driver = load_driver()
    return driver.node_register(node)

class OrchestrationDriver(object):
    '''Base class for orchestration driver.'''

    def register(self, node_id):
        """Register a node."""
        raise NotImplementedError()

    def boot(self, node_id):
        """Boot a node."""
        raise NotImplementedError()
