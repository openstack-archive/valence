import threading
import logging
import zmq
import time
from valence.db import api as db_api
import json
from valence.conductor.conductor import ComputeAPI as compute_api
import zerorpc

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

def sock_async():
    logging.debug(threading.currentThread().getName() + ' Starting')
    async_port = "5560"
    topic = "compute"
    context = zmq.Context()
    async_socket = context.socket(zmq.SUB)
    async_socket.connect ("tcp://localhost:%s" % async_port)
    async_socket.setsockopt(zmq.SUBSCRIBE, topic)
    while True:
        message = async_socket.recv()
        logging.debug("controller_server: Received message: " + str(message))
        message = message.split(":: ")
        topic_str = message[0]
        method_str = message[1]
        message = json.loads(message[2])
        method = getattr(compute_api, method_str)
        method(*(message.values()))
    logging.debug(threading.currentThread().getName() + ' Exiting')

def sock_sync():
    logging.debug(threading.currentThread().getName() + ' Starting')
    sync_port = "5561"
    s = zerorpc.Server(compute_api())
    s.bind("tcp://0.0.0.0:%s" %(sync_port))
    s.run()
    logging.debug(threading.currentThread().getName() + ' Exiting')

t = threading.Thread(name='controller_sync', target=sock_sync)
w = threading.Thread(name='controller_async', target=sock_async)

t.start()
w.start()
