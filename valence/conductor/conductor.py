from flavors import Flavor as flavors
from nodes import Node as nodes
from podmanagers import Podmanager as podmanagers


class ComputeAPI(object):
    @classmethod
    def list_flavors(cls):
        resp = flavors.list_flavors()
        return resp

    @classmethod
    def get_flavor(cls, flavorid):
        flavor = flavors.get_flavor(flavorid)
        return flavor

    @classmethod
    def create_flavor(cls, values):
        flavor = flavors.create_flavor(values)
        return flavor

    @classmethod
    def delete_flavor(cls, flavorid):
        resp = flavors.delete_flavor(flavorid)
        return resp

    @classmethod
    def update_flavor(cls, flavorid, values):
        flavor = flavors.update_flavor(flavorid, values)
        return flavor

    @classmethod
    def compose_node(cls, request_body):
        nodes.compose_node(request_body)

    @classmethod
    def manage_node(cls, request_body):
        resp = nodes.manage_node(request_body)
        return resp

    @classmethod
    def get_composed_node_by_uuid(cls, node_uuid):
        resp = nodes.get_composed_node_by_uuid(node_uuid)
        return resp

    @classmethod
    def delete_composed_node(cls, node_uuid):
        resp = nodes.delete_composed_node(node_uuid)
        return resp

    @classmethod
    def list_composed_nodes(cls):
        resp = nodes.list_composed_nodes()
        return resp

    @classmethod
    def node_action(cls, node_uuid, request_body):
        resp = nodes.node_action(node_uuid, request_body)
        return resp

    @classmethod
    def node_register(cls, node_uuid, request_body):
        resp = nodes.node_register(node_uuid, request_body)
        return resp

    @classmethod
    def get_podm_list(cls):
        return podmanagers.get_podm_list()

    @classmethod
    def get_podm_by_uuid(cls, uuid):
        return podmanagers.get_podm_by_uuid(uuid)

    @classmethod
    def create_podm(cls, values):
        return podmanagers.create_podm(values)

    @classmethod
    def update_podm(cls, uuid, values):
        return podmanagers.update_podm(uuid, values)

    @classmethod
    def delete_podm_by_uuid(cls, uuid):
        return podmanagers.delete_podm_by_uuid(uuid)

    @classmethod
    def get_podm_status(cls, url, authentication):
        return podmanagers.get_podm_status(url, authentication)
