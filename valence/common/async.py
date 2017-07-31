import logging

import futurist

LOG = logging.getLogger(__name__)
_EXECUTOR = None


def executor():
    global _EXECUTOR
    if not _EXECUTOR:
        _EXECUTOR = futurist.GreenThreadPoolExecutor(max_workers=10)
    return _EXECUTOR


def start_periodic_worker(callables):
    _periodics_worker = futurist.periodics.PeriodicWorker(
        callables=callables,
        executor_factory=futurist.periodics.ExistingExecutor(executor()))

    return executor().submit(_periodics_worker.start())


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
        raise


def async(func):
    """Start a job in new background thread.

    To start a async job, decorate the function as follows:
    Example:
        @async.async
        def test():
            pass
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
