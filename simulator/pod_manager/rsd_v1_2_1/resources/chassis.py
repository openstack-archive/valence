import uuid

from common import AuthResource
from resources import chassis_location
from resources import chassis_members
from resources import systems_members


class ChassisCollection(AuthResource):
    def get(self):
        return {
            "@odata.context": "/redfish/v1/$metadata#Chassis",
            "@odata.id": "/redfish/v1/Chassis",
            "@odata.type": "#ChassisCollection.ChassisCollection",
            "Name": "Chassis Collection",
            "Members@odata.count": 12,
            "Members": chassis_members
        }


class Chassis(AuthResource):
    def get(self, chassis_id):
        chassis_id = str(chassis_id)
        number = int(filter(str.isdigit, chassis_id))
        chassis_uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, chassis_id))

        # chassis hardware properties values
        manufacturer = 'Intel Corporaion'
        sku = chassis_uuid[:13]
        assert_tag = chassis_id
        serial_number = chassis_uuid[-12:]
        part_number = chassis_uuid[9:18]

        # Racks info
        if 'Rack' in chassis_id and number <= 2:
            name = 'Rack%s' % number
            chassis_type = 'Rack'
            model = 'Intel RSA Chassis-Rack'
            contained_by = 'Rack' + str(number)
            managed_by = '/redfish/v1/Chassis/rackManager' % number

            # rack contains content is chassis (chassis and drawers)
            if number == 1:
                contains_content = chassis_members[3:5] + \
                    chassis_members[6:7] + \
                    chassis_members[9:10]
            else:
                contains_content = chassis_members[5:6] + \
                    chassis_members[7:9] + \
                    chassis_members[10:]
            # Rack's computer systems
            # Rack1
            if number == 1:
                systems = systems_members[0: 28] + \
                    systems_members[42: 43] + \
                    systems_members[45: 46]
            # rack2
            else:
                systems = systems_members[28: 42] + \
                    systems_members[43: 45] + \
                    systems_members[46: 48]

        # Enclosures Chassis info
        elif 'Chassis' in chassis_id and number <= 3:
            name = 'FLEX-%s' % number
            chassis_type = 'Enclosure'
            model = 'Lenovo FLEX 8731'

            contained_by = 'Rack1' if number <= 2 else 'Rack2'
            managed_by = '/redfish/v1/Managers/BMC%d' % number

            # chassis contains content is systems, same with systems values
            sys_num = (number - 1) * 14
            systems = systems_members[sys_num: sys_num + 14]
            contains_content = systems

        # Drawers info
        elif 'Drawer' in chassis_id:
            name = 'ServerNode%s' % number
            chassis_type = 'Drawer'
            model = 'Lenovo System x3120'

            contained_by = 'Rack1' if number == 1 or number == 4 else 'Rack2'
            managed_by = '/redfish/v1/Managers/BMC%d' % (number + 3)

            sys_num = number + 41
            systems = systems_members[sys_num]
            contains_content = systems

        # Pod info
        elif 'Pod' in chassis_id:
            name = 'Pod1'
            chassis_type = 'Pod'
            model = 'Intel Pod Manager'

            manufacturer = 'Intel Corporaion'
            sku = ''
            assert_tag = ''
            serial_number = ''
            part_number = ''

            contained_by = 'Pod1'
            contains_content = chassis_members[1:3]
            managed_by = '/redfish/v1/Chassis/Pod1'
            systems = systems_members

        # Others not considered now
        else:
            return {}

        return {
            "@odata.context": "/redfish/v1/$metadata#Chassis/Members/$entity",
            "@odata.id": "/redfish/v1/Chassis/" + chassis_id,
            "@odata.type": "#Chassis.1.0.0.Chassis",
            "Id": chassis_id,
            "ChassisType": chassis_type,
            "Name": name,
            "Description": name,
            "Manufacturer": manufacturer,
            "Model": model,
            "SKU": sku,
            "SerialNumber": serial_number,
            "PartNumber": part_number,
            "AssetTag": assert_tag,
            "IndicatorLED": "On",
            "Status": {
                "State": "Enabled",
                "Health": "OK",
                "HealthRollup": "OK"
            },
            "Oem": {
                "Lenovo_RackScale": {
                    "@odata.type": "#Intel.Oem.Chassis",
                    "Location": {
                        "Rack": chassis_location[chassis_id][2],
                        "ULocation": chassis_location[chassis_id][0],
                        "UHeight": chassis_location[chassis_id][1],
                        "UWidth": '1 U'
                    },
                    "UUID": chassis_uuid
                }
            },
            "Links": {
                "Contains": contains_content,
                "ContainedBy": {
                    "@odata.id": "/redfish/v1/Chassis/%s" % contained_by
                },
                "ComputerSystems": systems,
                "Switches": [
                    {
                        "@odata.id": "/redfish/v1/EthernetSwitches/switch1"
                    }
                ],
                "ManagedBy": [
                    {
                        "@odata.id": managed_by
                    }
                ],
                "ManagersIn": [
                    {
                        "@odata.id": managed_by
                    }
                ],
                "Oem": {}
            }
        }
