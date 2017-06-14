import zerorpc
import time
import logging
import zmq
import json

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )


class ComputeAPI(object):

    @staticmethod
    def get_zerorpc_client():
        """" method returns zerorpc client used for synchronous RPC """
        sync_port = "5561"
        c = zerorpc.Client()
        c.connect("tcp://127.0.0.1:%s" %(sync_port))
        return c

    @staticmethod
    def call_async(message):
        """ method used for Asynchronous RPC """ 
        async_port = "5560"
        context = zmq.Context()
        async_socket = context.socket(zmq.PUB)
        async_socket.bind("tcp://*:%s" % async_port)
        time.sleep(1)
        logging.debug("controller_client: publishing data on topic ")
        topic = message["topic"]
        method = message["method"]
        del message["topic"]
        del message["method"]
        newmessage = "%s:: %s:: %s" %(topic, method, json.dumps(message))
        async_socket.send(newmessage)
        async_socket.close()
        context.destroy()


    @classmethod
    def list_flavors(cls):
        c = cls.get_zerorpc_client()
        flavor_models = c.list_flavors()
        c.close()
        return flavor_models

    @classmethod
    def get_flavor(cls, flavorid):
        c = cls.get_zerorpc_client()
        flavor = c.get_flavor(flavorid)
        c.close()
        return flavor

    @classmethod
    def create_flavor(cls, values):
        c = cls.get_zerorpc_client()
        flavor = c.create_flavor(values)
        c.close()
        return flavor

    @classmethod
    def delete_flavor(cls, flavorid):
        c = cls.get_zerorpc_client()
        res = c.delete_flavor(flavorid)
        c.close()
        return res

    @classmethod
    def update_flavor(cls, flavorid, values):
        c = cls.get_zerorpc_client()
        flavor = c.update_flavor(flavorid, values)
        c.close()
        return flavor

    @classmethod
    def compose_node(cls, topic, request_body):
        req = {
               "topic": topic,
               "method": "compose_node",
               "request_body": request_body
              } 
        cls.call_async(req) 

    @classmethod     
    def manage_node(cls, request_body):
        c = cls.get_zerorpc_client()
        res = c.manage_node(request_body)
        c.close()
        return res

    @classmethod
    def get_composed_node_by_uuid(cls, node_uuid):
        c = cls.get_zerorpc_client()
        res = c.get_composed_node_by_uuid(node_uuid)
        c.close()
        return res

    @classmethod
    def delete_composed_node(cls, node_uuid):
        c = cls.get_zerorpc_client()
        res = c.delete_composed_node(node_uuid)
        c.close()
        return res

    @classmethod 
    def list_composed_nodes(cls):
        c = cls.get_zerorpc_client()
        res = c.list_composed_nodes()
        c.close()
        return res

    @classmethod
    def node_action(cls, node_uuid, request_body):
        c = cls.get_zerorpc_client()
        res = c.node_action(node_uuid, request_body)
        c.close()
        return res

    @classmethod
    def node_register(cls, node_uuid, request_body):
        c = cls.get_zerorpc_client()
        res = c.node_register(node_uuid, request_body)
        c.close()
        return res 

    @classmethod
    def get_podm_list(cls):
        c = cls.get_zerorpc_client()
        res = c.get_podm_list()
        c.close()
        return res

    @classmethod
    def get_podm_by_uuid(cls, uuid):
        c = cls.get_zerorpc_client()
        res = c.get_podm_by_uuid(uuid)
        c.close()
        return res

    @classmethod
    def create_podm(cls, values):
        c = cls.get_zerorpc_client()
        res = c.create_podm(values)
        c.close()
        return res

    @classmethod
    def update_podm(cls, uuid, values):
        c = cls.get_zerorpc_client()
        res = c.update_podm(uuid, values)
        c.close()
        return res

    @classmethod
    def delete_podm_by_uuid(cls, uuid):
        c = cls.get_zerorpc_client()
        res = c.delete_podm_by_uuid(uuid)
        c.close()
        return res

    @classmethod
    def get_podm_status(cls, url, authentication):
        c = cls.get_zerorpc_client()
        res = c.get_podm_status(url, authentication)
        c.close()
        return res
