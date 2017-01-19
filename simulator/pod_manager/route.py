from simulator.pod_manager.resources import chassis
from simulator.pod_manager.resources import redfish_v1


def init_routes(api):
    pre = '/redfish/v1'
    api.add_resource(redfish_v1.Redfishv1Resource, pre)

    pre_chassis = '/redfish/v1/Chassis'
    api.add_resource(chassis.ChassisCollection, pre_chassis)
    api.add_resource(chassis.Chassis, pre_chassis + '/<string:chassis_id>')
