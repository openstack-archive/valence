import json
import threading
import time

from valence.conductor.conductor import ComputeAPI as compute_api
import valence.conf
from verboselogs import VerboseLogger as getLogger
import zerorpc
import zmq

logging = getLogger(__name__)
CONF = valence.conf.CONF


def sock_async():
    logging.debug(threading.currentThread().getName() + ' Starting')
    topic = CONF.conductor.compute_topic
    context = zmq.Context()
    async_socket = context.socket(zmq.SUB)
    async_socket.connect("tcp://%s:%s" % (CONF.conductor.bind_host,
                                          CONF.conductor.async_bind_port))
    async_socket.setsockopt(zmq.SUBSCRIBE, topic)
    while True:
        message = async_socket.recv()
        message = message.split(":: ")
        method_str = message[1]
        message = json.loads(message[2])
        method = getattr(compute_api, method_str)
        try:
            method(*(message['params']))
        except Exception:
            pass


def sock_sync():
    logging.debug(threading.currentThread().getName() + ' Starting')
    s = zerorpc.Server(compute_api())
    s.bind("tcp://0.0.0.0:%s" % (CONF.conductor.sync_bind_port))
    s.run()


def main():
    t = threading.Thread(name='conductor_sync', target=sock_sync)
    w = threading.Thread(name='conductor_async', target=sock_async)
    t.daemon = True
    w.daemon = True
    t.start()
    w.start()
    try:
        while True:
            time.sleep(1000)
    except(KeyboardInterrupt, SystemExit):
        return


if __name__ == "__main__":
    main()
