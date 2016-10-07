#!/usr/bin/env python
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

from oslo_config import cfg


# Configurations
podm_opts = [
    cfg.StrOpt('url',
               default='http://localhost:80',
               help=("The complete url string of PODM")),
    cfg.StrOpt('user',
               default='admin',
               help=("User for the PODM")),
    cfg.StrOpt('password',
               default='admin',
               help=("Passoword for PODM"))]

podm_conf_group = cfg.OptGroup(name='podm', title='RSC PODM options')
cfg.CONF.register_group(podm_conf_group)
cfg.CONF.register_opts(podm_opts, group=podm_conf_group)
