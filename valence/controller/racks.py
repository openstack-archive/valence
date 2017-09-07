# Copyright (c) 2016 Intel, Inc.
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


class Rack(object):

    def __init__(self, podm_id):
        self.connection = manager.get_connection(podm_id)

    def list_racks(self, request_body, filters={}):
        """List racks

        :param filters: filter params
        :param show_detail: True, to show detail info
        :return: rack list
        """
        return self.connection.list_racks(filters, request_body['show_detail'])

    def show_rack(self, rack_id):
        """Show rack

        :param rack_id: Rack ID
        :return: rack info
        """
        return self.connection.show_rack(rack_id)
