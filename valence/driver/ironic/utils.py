#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oslo_utils import uuidutils

from valence.common import clients
from valence.common import exception
from valence.common.i18n import _LE


def create_ironicclient():
    """Creates ironic client object.

        :param context: context to create client object
        :returns: Glance client object
    """
    osc = clients.OpenStackClients()
    print osc, osc.__dict__, "<<<<<<<<<<<<"
    return osc.ironic()
