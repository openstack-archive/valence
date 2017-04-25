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

from valence.common import exception
from valence.db import api as db_api

LOG = logging.getLogger(__name__)


def list_flavors():
    flavor_models = db_api.Connection.list_flavors()
    return [flavor.as_dict() for flavor in flavor_models]


def get_flavor(flavorid):
    flavor = db_api.Connection.get_flavor_by_uuid(flavorid)
    return flavor.as_dict()


def create_flavor(values):
    flavor = db_api.Connection.create_flavor(values)
    return flavor.as_dict()


def delete_flavor(flavorid):
    db_api.Connection.delete_flavor(flavorid)
    return exception.confirmation(
        confirm_code="DELETED",
        confirm_detail="This flavor {0} has been deleted successfully"
                       .format(flavorid))


def update_flavor(flavorid, values):
    flavor = db_api.Connection.update_flavor(flavorid, values)
    return flavor.as_dict()
