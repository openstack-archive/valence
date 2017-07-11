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

"""
Scheduler filters
"""


class BaseFilter(object):
    """Base class for pod manager filters."""

    def filter(self, host_state, filter_properties):
        """Return True if the pod manager passes the filter, otherwise False.
        Override this in a subclass.
        """
        raise NotImplementedError()


def all_filters():
    """Return a list of filter classes found in this directory.
    """
    pass
