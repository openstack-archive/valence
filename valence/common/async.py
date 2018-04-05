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

import futurist

from valence.common import exception

LOG = logging.getLogger(__name__)

_executor = None
_periodics_worker = None


def executor():
    global _executor
    if not _executor:
        _executor = futurist.GreenThreadPoolExecutor(max_workers=10)
    return _executor


def start_periodic_worker(callables):
    """Starts periodic execution of function passed in callables

    To enable this:
     1. Pass callables in following format:
         [(func, (arg1, arg2), {}), (func2, (arg1, arg2), {}),]

     2. Decorate func as follow:
        @periodics.periodic(spacing=2, enabled=True)
        def func(): pass

    :param callables: pass functions in this to execute periodically
    :returns: Future object
    """
    global _periodics_worker
    _periodics_worker = futurist.periodics.PeriodicWorker(
        callables=callables,
        executor_factory=futurist.periodics.ExistingExecutor(executor()))

    task_worker = executor().submit(_periodics_worker.start)
    task_worker.add_done_callback(_handle_exceptions)


def stop_periodic_tasks():
    """Stops all periodic tasks and cleanup resources. """

    global _periodics_worker
    if _periodics_worker is not None:
        try:
            _periodics_worker.stop()
            _periodics_worker.wait()
        except Exception:
            LOG.exception("Exception occurred when stopping periodic workers")
        _periodics_worker = None

    if _executor and _executor.alive:
        _executor.shutdown(wait=True)

    LOG.debug("periodic tasks stopped successfully")


def _spawn_worker(func, *args, **kwargs):

    """Creates a greenthread to run func(*args, **kwargs).

    Spawns a greenthread if there are free slots in pool, otherwise raises
    exception. Execution control returns immediately to the caller.

    :returns: Future object.
    :raises: NoFreeWorker if worker pool is currently full.
    """
    try:
        return executor().submit(func, *args, **kwargs)
    except futurist.RejectedSubmission:
        raise exception.ValenceException("No free worker available")


def async(func):
    """Start a job in new background thread.

    To start a async job, decorate the function as follows:
        @async.async
        def test(): pass
    """
    def wrapper(*args, **kwargs):
        LOG.info("starting async thread for function %s", func.__name__)
        future = _spawn_worker(func, *args, **kwargs)
        future.add_done_callback(_handle_exceptions)
    return wrapper


def _handle_exceptions(fut):
    try:
        fut.result()
    except Exception:
        msg = 'Unexpected exception in background thread'
        LOG.exception(msg)
