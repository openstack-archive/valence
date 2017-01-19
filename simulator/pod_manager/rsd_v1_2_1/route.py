from resources import chassis
from resources import composed_node
from resources import computer_system
from resources import redfish_v1


def init_routes(api):
    pre = '/redfish/v1'
    api.add_resource(redfish_v1.Redfishv1Resource, pre)

    pre_chassis = '/redfish/v1/Chassis'
    api.add_resource(chassis.ChassisCollection, pre_chassis)
    api.add_resource(chassis.Chassis, pre_chassis + '/<string:chassis_id>')

    pre_systems = '/redfish/v1/Systems'
    api.add_resource(computer_system.SystemCollection, pre_systems)
    api.add_resource(computer_system.System,
                     pre_systems + '/<string:system_id>')

    pre_nodes = '/redfish/v1/Nodes'
    api.add_resource(composed_node.NodeCollection, pre_nodes)
    api.add_resource(composed_node.Node, pre_nodes + '/<string:node_id>')
