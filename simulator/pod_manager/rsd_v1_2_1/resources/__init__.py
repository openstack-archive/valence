import sys
sys.path.append("..")  # noqa

import uuid

from common import generate_members


# init system and nodes numbers
systems_num = 48
nodes_num = 6

# cache for components info
computer_systems = {}
composed_nodes = {}

# init components collection info
systems_members = generate_members('System',
                                   '/redfish/v1/Systems/',
                                   systems_num)

nodes_members = generate_members('Node', '/redfish/v1/Nodes/', 6)

chassis_members = generate_members("Pod", "/redfish/v1/Chassis/", 1) \
    + generate_members("Rack", "/redfish/v1/Chassis/", 2) \
    + generate_members("Chassis", "/redfish/v1/Chassis/", 3) \
    + generate_members("Drawer", "/redfish/v1/Chassis/", 6)


# init hardware locations info
chassis_location = {
    'Pod1': ['', '', ''],
    'Rack1': ['', '', 'Pod1'],
    'Rack2': ['', '', 'Pod1'],
    'Chassis1': ['25 U', '10 U', 'Rack1'],
    'Chassis2': ['6 U', '10 U', 'Rack1'],
    'Chassis3': ['11 U', '10 U', 'Rack2'],
    'Drawer1': ['19 U', '2 U', 'Rack1'],
    'Drawer2': ['34 U', '2 U', 'Rack2'],
    'Drawer3': ['32 U', '2 U', 'Rack2'],
    'Drawer4': ['17 U', '1 U', 'Rack1'],
    'Drawer5': ['26 U', '1 U', 'Rack2'],
    'Drawer6': ['25 U', '1 U', 'Rack2'],
}


# Hardware distribution map : http://imgur.com/a/FP4c9
def generate_computer_systems():
    for number in range(1, systems_num+1):
        system_id = 'System%d' % number
        system_url = '/redfish/v1/Systems/%s' % system_id
        system_uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, system_id))
        sku = system_uuid[:13]
        assert_tag = 'asset tag%s' % system_id
        serial_number = system_uuid[-12:]
        part_number = system_uuid[9:18]
        manufacturer = 'Dual socket Xeon Server'

        if 43 <= number <= 48:
            type_ = 'Logical'
            name = 'ServerNode%d' % (number - 42)
            description = 'Nova node%d' % (number - 42)
            model = 'Lenovo System x3120' if number <= 45 else \
                'Lenovo System x3650'
            hostname = 'nova-%d' % (number - 42)
            chassis_id = 'Drawer%d' % (number - 42)
            managed_by = '/redfish/v1/Managers/BMC%d' % (number - 39)
            u_location = chassis_location[chassis_id][0]
            system_location = 1
            u_height = chassis_location[chassis_id][1]
            u_width = '1 U'
        else:
            type_ = 'Physical'
            name = 'LTE-%d' % number
            description = 'Nova node%d' % number
            model = 'Lenovo System x3120' if number <= 8 else \
                'Lenovo System x3650'
            hostname = 'nova-%d' % number
            system_location = number % 14 if number % 14 != 0 else 14
            u_height = '1 U'
            u_width = '0.5 U'

            # Chassis1's computer system
            if 29 <= number <= 42:
                chassis_id = 'Chassis3'
                managed_by = '/redfish/v1/Managers/BMC3'

            # Chassis1's computer system
            elif 15 <= number <= 28:
                chassis_id = 'Chassis2'
                managed_by = '/redfish/v1/Managers/BMC2'

            # Chassis1's computer system
            else:
                chassis_id = 'Chassis1'
                managed_by = '/redfish/v1/Managers/BMC1'

            base_u_location = chassis_location[chassis_id][0]
            base_u_num = int(filter(str.isdigit, base_u_location))
            u_location = '%d U' % ((system_location + 1) / 2 + base_u_num)

        system_info = {
            "@odata.context": "/redfish/v1/$metadata#Systems/Members/$entity",
            "@odata.id": system_url,
            "@odata.type": "#ComputerSystem.1.0.0.ComputerSystem",
            "Id": system_id,
            "Name": name,
            "SystemType": type_,
            "AssetTag": assert_tag,
            "Manufacturer": manufacturer,
            "Model": model,
            "SKU": sku,
            "SerialNumber": serial_number,
            "PartNumber": part_number,
            "Description": description,
            "UUID": system_uuid,
            "HostName": hostname,
            "Status": {
                "State": "Enabled",
                "Health": "OK",
                "HealthRollUp": "OK"
            },
            "IndicatorLED": "On",
            "PowerState": "On",
            "Boot": {
                "BootSourceOverrideEnabled": "Once",
                "BootSourceOverrideTarget": "Pxe",
                "BootSourceOverrideTarget@Redfish.AllowableValues": ["None",
                                                                     "Pxe",
                                                                     "Hdd"],
            },
            "BiosVersion": "P79 v1.00",
            "ProcessorSummary": {
                "Count": 2,
                "Model": "Multi-Core Intel(R) Xeon(R) processor 7xxx Series",
                "Status": {
                    "State": "Enabled",
                    "Health": "OK",
                    "HealthRollUp": "OK"
                }
            },
            "MemorySummary": {
                "TotalSystemMemoryGiB": 64,
                "Status": {
                    "State": "Enabled",
                    "Health": "OK",
                    "HealthRollUp": "OK"
                }
            },
            "Processors": {
                "@odata.id": "/redfish/v1/Systems/%s/Processors" % system_id},
            "EthernetInterfaces": {
                "@odata.id": "/redfish/v1/Systems/%s/EthernetInterfaces" %
                             system_id
            },
            "SimpleStorage": {},
            "DimmConfig": {
                "@odata.id": "/redfish/v1/Systems/%s/DimmConfig" % system_id
            },
            "MemoryChunks": {
                "@odata.id": "/redfish/v1/Systems/%s/MemoryChunk" % system_id
            },
            "Links": {
                "Chassis": [{
                    "@odata.id": "/redfish/v1/Chassis/%s" % chassis_id
                }],
                "ManagedBy": [{
                    "@odata.id": managed_by
                }],
                "Oem": {}
            },
            "Actions": {
                "#ComputerSystem.Reset": {
                    "target":
                        "/redfish/v1/Systems/%s/Actions/ComputerSystem.Reset" %
                        system_id,
                    "ResetType@Redfish.AllowableValues": [
                        "On",
                        "ForceOff",
                        "GracefulShutdown",
                        "ForceRestart",
                        "Nmi",
                        "GracefulRestart",
                        "ForceOn",
                        "PushPowerButton"]
                },
                "Oem": {
                    "Lenovo_RackScale": {
                        "#ComputerSystem.StartDeepDiscovery": {
                            "target":
                                "/redfish/v1/Systems/%s/Actions/ComputerSystem"
                                ".StartDeepDiscovery" % system_id
                        },
                    }
                }
            },
            "Oem": {
                "Lenovo_RackScale": {
                    "SystemLocation": system_location,
                    "Location": {
                        "ULocation": u_location,
                        "UHeight": u_height,
                        "UWidth": u_width,
                        "Chassis": chassis_id
                    },
                    "@odata.type": "#Intel.Oem.ComputerSystem",
                    "Adapters": {
                        "@odata.id": "/redfish/v1/Systems/%s/Adapters" %
                                     system_id
                    },
                    "PciDevices": [{
                        "VendorId": "0x8086",
                        "DeviceId": "0x1234"
                    }],
                    "DiscoveryState": "Basic",
                    "ProcessorSockets": 8, "MemorySockets": 8
                }
            }
        }
        computer_systems[system_url] = system_info


# Hardware distribution map : http://imgur.com/a/FP4c9
def generate_composed_nodes():
    for number in range(1, 7):
        node_id = 'Node%d' % number
        node_url = "/redfish/v1/Nodes/Node%d" % number
        name = 'composedNode%d' % number
        description = 'Nova node%s' % number

        system_url = "/redfish/v1/Systems/System%d" % (number + 42)
        system_info = computer_systems[system_url]

        node_info = {
            "@odata.context": "/redfish/v1/$metadata#Nodes/Members/$entity",
            "@odata.id": node_url,
            "@odata.type": "#ComposedNode.1.0.0.ComposedNode",
            "Id": node_id,
            "Name": name,
            "Description": description,
            "SystemType": "Logical",
            "AssetTag": "free form asset tag",
            "Manufacturer": system_info['Manufacturer'],
            "Model": system_info['Model'],
            "SKU": system_info['SKU'],
            "SerialNumber": system_info['SerialNumber'],
            "PartNumber": system_info['PartNumber'],
            "UUID": system_info['UUID'],
            "HostName": system_info['HostName'],
            "PowerState": "On",
            "BiosVersion": system_info['BiosVersion'],
            "Status": {
                "State": "Enabled",
                "Health": "OK",
                "HealthRollUp": "OK"
            },
            "Processors": {
                "Count": 2,
                "Model": "Multi-Core Intel(R) Xeon(R) processor 7xxx Series",
                "Status": {
                    "State": "Enabled",
                    "Health": "OK"
                }
            },
            "Memory": {
                "TotalSystemMemoryGiB": 64,
                "Status": {
                    "State": "Enabled",
                    "Health": "OK"
                }
            },
            "ComposedNodeState": "Allocated",
            "Boot": {
                "BootSourceOverrideEnabled": "Disabled",
                "BootSourceOverrideTarget": "None",
                "BootSourceOverrideTarget@Redfish.AllowableValues": [
                    "None",
                    "Pxe",
                    "Hdd"
                ]
            },
            "Oem": {},
            "Links": {
                "ComputerSystem": {
                    "@odata.id": system_url
                },
                "Processors": [
                    {
                        "@odata.id": "%s/Processors/CPU1" % system_url
                    },
                    {
                        "@odata.id": "%s/Processors/CPU2" % system_url
                    }
                ],
                "Memory": [
                    {
                        "@odata.id": "%s/DimmConfig/Dimm1" % system_url
                    },
                    {
                        "@odata.id": "%s/DimmConfig/Dimm2" % system_url
                    },
                    {
                        "@odata.id": "%s/DimmConfig/Dimm3" % system_url
                    },
                    {
                        "@odata.id": "%s/DimmConfig/Dimm4" % system_url
                    }
                ],
                "EthernetInterfaces": [
                    {
                        "@odata.id": "%s/EthernetInterfaces/LAN1" % system_url
                    }
                ],
                "LocalDrives": [
                    {
                        "@odata.id": "%s/StorageControllers/"
                                     "Controller1/Drives/Drive1" % system_url
                    }
                ],
                "RemoteDrives": [
                    {
                        "@odata.id": "/redfish/v1/Services/RSS1/Targets/target"
                    }
                ],
                "ManagedBy": [
                    {
                        "@odata.id": "/redfish/v1/Managers/PODM"
                    }
                ],
                "Oem": {}
            },
            "Actions": {
                "#ComposedNode.Reset": {
                    "target": "%s/Actions/ComposedNode.Reset" % system_url,
                    "ResetType@Redfish.AllowableValues": [
                        "On",
                        "ForceOff",
                        "GracefulRestart",
                        "ForceRestart",
                        "Nmi",
                        "ForceOn",
                        "PushPowerButton",
                        "GracefulShutdown"
                    ]
                },
                "#ComposedNode.Assemble": {
                    "target": "%s/Actions/ComposedNode.Assemble" % system_url
                }
            }
        }
        composed_nodes[node_url] = node_info


def init_data_generation():
    generate_computer_systems()
    generate_composed_nodes()
