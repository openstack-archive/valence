from flask_restful import Resource

from simulator.pod_manager.resources import nodes_members


class Nodes(Resource):
    def get(self):
        return {
            "@odata.context": "/redfish/v1/$metadata#ComposedNodeCollection.ComposedNodeCollection",
            "@odata.id": "/redfish/v1/Nodes",
            "@odata.type": "#ComposedNodeCollection.CComposedNodeCollection",
            "Name": "Composed Node Collection",
            "Members@odata.count": 6,
            "Members": nodes_members
        }


class NodeDetail(Resource):
    def get(self):
        pass


