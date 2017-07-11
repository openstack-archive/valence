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
import random

from valence.common import exception
from valence import conf

CONF = conf.CONF
LOG = logging.getLogger(__name__)


class Scheduler(object):
    """Scheduler that can be used for filtering and prioritizing."""
    def __init__(self, *args, **kwargs):
        pass

    def _get_all_podm_states(self):
        pass

    def schedule(self, spec_obj):
        """Returns a sorted list of HostState objects that satisfy the
        supplied request_spec.
        """

        pod_managers = self._get_all_podm_states()

        if not pod_managers:
            reason = 'There is no pod manager available.'
            LOG.debug(reason)
            raise exception.NoValidHost(reason=reason)

        selected_podm = self._schedule(spec_obj, pod_managers)

        if not selected_podm:
            LOG.debug('There are several pod managers available but no valid'
                      'one satisfy the request.')
            reason = 'These is no pod manager satisfy the request.'
            raise exception.NoValidHost(reason=reason)

        return selected_podm

    def _schedule(self, spec_obj, pod_managers):
        """Returns a list of hosts that meet the required specs,
        ordered by their fitness.
        """

        # Filter pod manager based on requirements.
        filtered_podm = self._filter_podm(spec_obj, pod_managers)
        LOG.debug("Filtered %(podm)s", {'podm': filtered_podm})

        weighed_podm = self._prioritizer_podm(spec_obj, filtered_podm)
        LOG.debug("Weighed %(podm)s", {'podm': weighed_podm})

        chosen_podm = random.choice(weighed_podm)
        LOG.debug("Selected host: %(podm)s", {'podm': chosen_podm})

        return chosen_podm

    def _filter_podm(self, spec_obj, pod_managers):
        pass

    def _prioritizer_podm(self, spec_obj, pod_managers):
        pass
