# Copyright 2016 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""This Module reads the configuration from .conf file
   and set default values if the expected values are not set

"""

import logging

from six.moves import configparser


def get_option(section, key, default, type=str):
    """Function to support default values

    Though config fallback feature could be used
    Py 2.7 doesnt support it

    """
    if config.has_option(section, key):
        return type(config.get(section, key))
    else:
        return type(default)


PROJECT_NAME = 'valence'

config_file = "/etc/%s/%s.conf" % (PROJECT_NAME, PROJECT_NAME)
config = configparser.ConfigParser()
config.read(config_file)

# Log settings
log_level_map = {'debug': logging.DEBUG,
                 'info': logging.INFO,
                 'warning': logging.WARNING,
                 'error': logging.ERROR,
                 'critical': logging.CRITICAL,
                 'notset': logging.NOTSET}

log_default_loc = "/var/log/%s/%s.log" % (PROJECT_NAME, PROJECT_NAME)
log_default_format = "%(asctime)s %(name)-4s %(levelname)-4s %(message)s"
log_level_name = get_option("DEFAULT", "log_level", 'error')

log_file = get_option("DEFAULT", "log_file", log_default_loc)
log_level = log_level_map.get(log_level_name.lower())
log_format = get_option("DEFAULT", "log_format", log_default_format)

# Server Settings
bind_port = get_option("DEFAULT", "bind_port", 8181, int)
bind_host = get_option("DEFAULT", "bind_host", "0.0.0.0")
debug = get_option("DEFAULT", "debug", False, bool)

# PODM Settings
podm_url = get_option("podm", "url", "http://127.0.0.1")
podm_user = get_option("podm", "user", "admin")
podm_password = get_option("podm", "password", "admin")
redfish_base_ext = get_option("podm", "redfish_base_ext", "/redfish/v1/")

# Database etcd Settings
etcd_host = get_option("database_etcd", "host", "localhost")
etcd_port = get_option("database_etcd", "port", 2379, int)
