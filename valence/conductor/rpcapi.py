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

import json
import time

import valence.conf
from verboselogs import VerboseLogger as getLogger
import zerorpc
import zmq

logging = getLogger(__name__)
CONF = valence.conf.CONF


class ComputeAPI(object):

    @staticmethod
    def get_zerorpc_client():
        """Method returns zerorpc client used for synchronous RPC

        """

        c = zerorpc.Client(timeout=300, heartbeat=60)
        c.connect("tcp://%s:%s" % (CONF.conductor.bind_host,
                                   CONF.conductor.sync_bind_port))
        return c

    @staticmethod
    def call_async(message):
        """Method used for Asynchronous RPC

        """

        context = zmq.Context()
        async_socket = context.socket(zmq.PUB)
        async_socket.bind("tcp://*:%s" % (CONF.conductor.async_bind_port))
        time.sleep(1)
        topic = message["topic"]
        method = message["method"]
        logging.debug("rpcapi: publishing data on topic %s " % (topic))
        del message["topic"]
        del message["method"]
        newmessage = "%s:: %s:: %s" % (topic, method, json.dumps(message))
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
    def list_tasks(cls):
        c = cls.get_zerorpc_client()
        tasks = c.list_tasks()
        c.close()
        return tasks

    @classmethod
    def get_task(cls, task_uuid):
        c = cls.get_zerorpc_client()
        task = c.get_task(task_uuid)
        c.close()
        return task

    @classmethod
    def create_task(cls, request, *args):
        c = cls.get_zerorpc_client()
        task = c.create_task(request, *args)
        c.close()
        return task

    @classmethod
    def delete_task(cls, task_uuid):
        c = cls.get_zerorpc_client()
        res = c.delete_task(task_uuid)
        c.close()
        return res

    @classmethod
    def update_task(cls, task_uuid, err=None):
        c = cls.get_zerorpc_client()
        res = c.update_task(task_uuid, err)
        c.close()
        return res

    @classmethod
    def compose_node(cls, req):
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
