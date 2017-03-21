#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from valence.common import clients


def create_ironicclient():
    """Creates ironic client object.

        :param context: context to create client object
        :returns: Glance client object
    """
    osc = clients.OpenStackClients()
    return osc.ironic()
