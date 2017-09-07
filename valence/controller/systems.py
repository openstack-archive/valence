# Copyright (c) 2017 NEC, Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
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

import logging

from valence.podmanagers import manager

LOG = logging.getLogger(__name__)


class System(object):

    def __init__(self, podm_id):
        self.connection = manager.get_connection(podm_id)

    def list_systems(self, filters={}):
        """List racks

        :param filters: filter params
        :param show_detail: True, to show detail info
        :return: rack list
        """
        return self.connection.systems_list(filters)

    def get_system_by_id(self, system_id):
        """Show rack

        :param rack_id: Rack ID
        :return: rack info
        """
        return self.connection.get_system_by_id(system_id)
