from simulator.pod_manager.rsd_v1_2_1.common import AuthResource
from simulator.pod_manager.rsd_v1_2_1.resources import computer_systems
from simulator.pod_manager.rsd_v1_2_1.resources import systems_members


class SystemCollection(AuthResource):
    def get(self):
        return {
            "@odata.context": "/redfish/v1/$metadata#ComputerSystemCollection."
                              "ComputerSystemCollection",
            "@odata.id": "/redfish/v1/Systems",
            "@odata.type": "ComputerSystemCollection.ComputerSystemCollection",
            "Name": "Computer System Collection",
            "Members@odata.count": 48,
            "Members": systems_members
        }


class System(AuthResource):
    def get(self, system_id):
        system_url = '/redfish/v1/Systems/%s' % system_id
        return computer_systems[system_url]
