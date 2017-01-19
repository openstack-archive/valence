from simulator.pod_manager.rsd_v1_2_1.common import AuthResource
from simulator.pod_manager.rsd_v1_2_1.resources import composed_nodes
from simulator.pod_manager.rsd_v1_2_1.resources import nodes_members


class NodeCollection(AuthResource):
    def get(self):
        return {
            "@odata.context": "/redfish/v1/$metadata#ComposedNodeCollection."
                              "ComposedNodeCollection",
            "@odata.id": "/redfish/v1/Nodes",
            "@odata.type": "#ComposedNodeCollection.CComposedNodeCollection",
            "Name": "Composed Node Collection",
            "Members@odata.count": 6,
            "Members": nodes_members
        }


class Node(AuthResource):
    def get(self, node_id):
        node_url = '/redfish/v1/Systems/%s' % node_id
        return composed_nodes[node_url]
