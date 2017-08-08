# Copyright (c) 2017 Intel, Inc.
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

from oslo_config import cfg

from valence.conf import api
from valence.conf import default
from valence.conf import etcd
from valence.conf import ironic_client
from valence.conf import podm

CONF = cfg.CONF

default.register_opts(CONF)
api.register_opts(CONF)
etcd.register_opts(CONF)
ironic_client.register_opts(CONF)
podm.register_opts(CONF)
