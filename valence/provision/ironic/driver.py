# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
import six

from oslo_log import log as logging

from valence.common import exception
import valence.conf
from valence.controller import nodes
from valence.db import api as db_api
from valence.provision import driver
from valence.provision.ironic import utils
from valence.redfish import redfish

CONF = valence.conf.CONF

LOG = logging.getLogger(__name__)


class IronicDriver(driver.OrchestrationDriver):

    def __init__(self):
        super(IronicDriver, self).__init__()

    def node_register(self, node_uuid):
        LOG.debug('Registering node %s to ironic' % node_uuid)
        try:
            ironic = utils.create_ironicclient()
            system = redfish.systems_list()
            driver_info = {
                'redfish_root_uri': requests.compat.urljoin(
                    CONF.podm.url, CONF.podm.base_ext),
                'redfish_username': CONF.podm.username,
                'redfish_password': CONF.podm.password,
                'redfish_verify_ca': CONF.podm.verify_ca,
                'redfish_system_id': system[0]['id']}
            node_info = nodes.Node.get_composed_node_by_uuid(node_uuid)
            node_args = {'driver': 'redfish', 'name': node_info['name'],
                         'driver_info': driver_info}
            ironic_node = ironic.node.create(**node_args)
            port_args = {'node_uuid': ironic_node.uuid,
                         'address': node_info['metadata']['network'][0]['mac']}
            ironic.port.create(**port_args)
            db_api.Connection.update_composed_node(node_uuid,
                                                   {'managed_by': 'ironic'})
            return "Node created at Ironic"
        except Exception as e:
            message = ('Unexpected error while registering node at '
                       'Ironic: %s' % six.text_type(e))
            LOG.error(message)
            raise exception.ValenceException(message, e.http_status)
