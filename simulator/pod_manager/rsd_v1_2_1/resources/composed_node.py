from common import AuthResource
from resources import composed_nodes
from resources import nodes_members
from resources import nodes_num


class NodeCollection(AuthResource):
    def get(self):
        return {
            "@odata.context": "/redfish/v1/$metadata#ComposedNodeCollection."
                              "ComposedNodeCollection",
            "@odata.id": "/redfish/v1/Nodes",
            "@odata.type": "#ComposedNodeCollection.CComposedNodeCollection",
            "Name": "Composed Node Collection",
            "Members@odata.count": nodes_num,
            "Members": nodes_members
        }


class Node(AuthResource):
    def get(self, node_id):
        node_url = '/redfish/v1/Nodes/%s' % node_id
        return composed_nodes[node_url]
