# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import six

from oslo_log import log as logging

from valence.common import exception
from valence.common.i18n import _
from valence.common import utils as common_utils
import valence.conf
from valence.driver import driver
from valence.driver.ironic import utils

CONF = valence.conf.CONF

LOG = logging.getLogger(__name__)


class IronicDriver(driver.OrchestrationDriver):

    def __init__(self):
        super(IronicDriver, self).__init__()

    def node_register(self, node_id):
        LOG.debug('Registering node %s to ironic' % node_id)
        try:
            ironic = utils.create_ironicclient()
            driver_info = {'redfish_root_uri': CONF.podm.url+CONF.podm.base_ext, 'redfish_username': CONF.podm.username, 'redfish_password': CONF.podm.password, 'redfish_verify_ca': False, 'redfish_system_id': 1}
            args = {'driver': 'redfish', 'uuid': node_id, 'name': 'valence-node', 'driver_info': driver_info}
            resp = ironic.node.create(**args)
            return resp
        except Exception as e:
            msg = _('Cannot download image from ironic: {0}')
            #raise exception.ValenceException(msg.format(e))
            print e, "Exception"
            raise
