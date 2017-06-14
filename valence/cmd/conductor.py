import json
import logging
import threading

from valence.conductor.conductor import ComputeAPI as compute_api
import zerorpc
import zmq

LOG = logging.getLogger(__name__)


def sock_async():
    LOG.debug(threading.currentThread().getName() + ' Starting')
    async_port = "5560"
    topic = "compute"
    context = zmq.Context()
    async_socket = context.socket(zmq.SUB)
    async_socket.connect("tcp://localhost:%s" % async_port)
    async_socket.setsockopt(zmq.SUBSCRIBE, topic)
    while True:
        message = async_socket.recv()
        LOG.debug("controller_server: Received message: " + str(message))
        message = message.split(":: ")
        method_str = message[1]
        message = json.loads(message[2])
        method = getattr(compute_api, method_str)
        method(*(message.values()))
    LOG.debug(threading.currentThread().getName() + ' Exiting')


def sock_sync():
    LOG.debug(threading.currentThread().getName() + ' Starting')
    sync_port = "5561"
    s = zerorpc.Server(compute_api())
    s.bind("tcp://0.0.0.0:%s" % (sync_port))
    s.run()
    LOG.debug(threading.currentThread().getName() + ' Exiting')

t = threading.Thread(name='controller_sync', target=sock_sync)
w = threading.Thread(name='controller_async', target=sock_async)

t.start()
w.start()
