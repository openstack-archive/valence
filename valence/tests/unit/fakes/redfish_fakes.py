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


def mock_request_get(json_data, status_code):

    class MockResponse(object):
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    return MockResponse(json_data, status_code)


def fake_service_root():
    return {
        "@odata.id": "/redfish/v1",
        "Id": "ServiceRoot",
        "Name": "Service root",
        "RedfishVersion": "1.0.0",
        "Chassis": {
            "@odata.id": "/redfish/v1/Chassis"
        },
        "Services": {
            "@odata.id": "/redfish/v1/Services"
        },
        "Systems": {
            "@odata.id": "/redfish/v1/Systems"
        },
        "Managers": {
            "@odata.id": "/redfish/v1/Managers"
        },
        "Nodes": {
            "@odata.id": "/redfish/v1/Nodes"
        },
        "EthernetSwitches": {
            "@odata.id": "/redfish/v1/EthernetSwitches"
        }
    }


def fake_nodes_root():
    return {
        "@odata.context": "/redfish/v1/$metadata#Nodes",
        "@odata.id": "/redfish/v1/Nodes",
        "@odata.type": "#ComposedNodeCollection.ComposedNodeCollection",
        "Name": "Composed Nodes Collection",
        "Members@odata.count": 1,
        "Members": [{
            "@odata.id": "/redfish/v1/Nodes/14"
        }],
        "Actions": {
            "#ComposedNodeCollection.Allocate": {
                "target": "/redfish/v1/Nodes/Actions/Allocate"
            }
        }
    }


def fake_node_detail():
    return {
        "@odata.context": "/redfish/v1/$metadata#Nodes/Members/$entity",
        "@odata.id": "/redfish/v1/Nodes/6",
        "@odata.type": "#ComposedNode.1.0.0.ComposedNode",
        "Id": "6",
        "Name": "test",
        "Description": "",
        "SystemType": "Logical",
        "AssetTag": "",
        "Manufacturer": "",
        "Model": "",
        "SKU": "",
        "SerialNumber": "",
        "PartNumber": "",
        "UUID": "deba2630-d2af-11e6-a65f-4d709ab9a725",
        "HostName": "web-srv344",
        "PowerState": "On",
        "BiosVersion": "P79 v1.00 (09/20/2013)",
        "Status": {
            "State": "Enabled",
            "Health": "OK",
            "HealthRollup": "OK"
        },
        "Processors": {
            "Count": 1,
            "Status": {
                "State": "Enabled",
                "Health": "OK",
                "HealthRollup": "OK"
            }
        },
        "Memory": {
            "TotalSystemMemoryGiB": 8,
            "Status": {
                "State": "Enabled",
                "Health": "OK",
                "HealthRollup": "OK"
            }
        },
        "ComposedNodeState": "PoweredOff",
        "Boot": {
            "BootSourceOverrideEnabled": "Continuous",
            "BootSourceOverrideTarget": "Hdd",
            "BootSourceOverrideTarget@Redfish.AllowableValues": [
                "None", "Pxe", "Floppy", "Cd", "Usb", "Hdd", "BiosSetup",
                "Utilities", "Diags", "UefiTarget"]
        },
        "Oem": {},
        "Links": {
            "ComputerSystem": {
                "@odata.id": "/redfish/v1/Systems/1"
            },
            "Processors": [{
                "@odata.id": "/redfish/v1/Systems/1/Processors/1"
            }],
            "Memory": [{
                "@odata.id": "/redfish/v1/Systems/1/Memory/1"
            }],
            "EthernetInterfaces": [{
                "@odata.id": "/redfish/v1/Systems/1/EthernetInterfaces/2"
            }],
            "LocalDrives": [],
            "RemoteDrives": [],
            "ManagedBy": [{
                "@odata.id": "/redfish/v1/Managers/1"
            }],
            "Oem": {}
        },
        "Actions": {
            "#ComposedNode.Reset": {
                "target": "/redfish/v1/Nodes/6/Actions/ComposedNode.Reset",
                "ResetType@DMTF.AllowableValues": [
                    "On", "ForceOff", "GracefulShutdown", "ForceRestart",
                    "Nmi", "GracefulRestart", "ForceOn", "PushPowerButton"]
            },
            "#ComposedNode.Assemble": {
                "target": "/redfish/v1/Nodes/6/Actions/ComposedNode.Assemble"
            }
        }
    }


def fake_chassis_list():
    return [
        {
            "Id": "1",
            "ChassisType": "Pod",
            "Name": "Pod 1"
        },
        {
            "Id": "2",
            "ChassisType": "Rack",
            "Name": "Rack 1"
        },
        {
            "Id": "3",
            "ChassisType": "Rack",
            "Name": "Rack 2"
        }
    ]


def fake_processor_list():
    return [
        {
            "Id": "1",
            "TotalCores": 1,
            "InstructionSet": "x86",
            "Model": "Intel Xeon"
        },
        {
            "Id": "2",
            "TotalCores": 2,
            "InstructionSet": "x86",
            "Model": "Intel Xeon"
        }
    ]


def fake_detailed_system():
    return {
        "@odata.id": "/redfish/v1/Systems/1",
        "Id": "1",
        "Name": "Fake System",
        "SystemType": "Physical",
        "Status": {
            "State": "Enabled",
            "Health": "OK"
        },
        "PowerState": "On",
        "ProcessorSummary": {
            "Count": "1",
            "Model": "Intel Xeon",
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        "MemorySummary": {
            "TotalSystemMemoryGiB": 8,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        }
    }


def fake_simple_storage():
    return {
        "@odata.id": "/redfish/v1/Systems/1/SimpleStorage/1",
        "Id": "1",
        "Name": "Simple Storage Controller",
        "Devices": [
            {
                "Name": "Drive 1",
                "CapacityBytes": 322122547200
            },
            {
                "Name": "Drive 2",
                "CapacityBytes": 322122547200
            }
        ]
    }


def fake_processor():
    return {
        "InstructionSet": "x86-64",
        "Model": "Intel(R) Core(TM) i7-4790",
        "MaxSpeedMHz": 3700,
        "TotalCores": 8,
    }


def fake_memory():
    return {
        "DataWidthBits": 0,
        "OperatingSpeedMhz": 2400,
        "CapacityMiB": 8192
    }


def fake_network_interface():
    return {
        "MACAddress": "e9:47:d3:60:64:66",
        "SpeedMbps": 100,
        "Status": {
            "State": "Enabled"
        },
        "IPv4Addresses": [{
            "Address": "192.168.0.10",
            "SubnetMask": "255.255.252.0",
            "Gateway": "192.168.0.1",
        }],
        "VLANs": {
            "@odata.id": "/redfish/v1/Systems/1/EthernetInterfaces/2/VLANs"
        }
    }


def fake_vlan():
    return {
        "VLANId": 99,
        "Status": {
            "State": "Enabled",
        }
    }


def fake_system_ethernet_interfaces():
    return {
        "@odata.id": "/redfish/v1/Systems/1/EthernetInterfaces",
        "Name": "Ethernet Interface Collection",
        "Members@odata.count": 2,
        "Members": [
            {"@odata.id": "/redfish/v1/Systems/1/EthernetInterfaces/1"},
            {"@odata.id": "/redfish/v1/Systems/1/EthernetInterfaces/2"}
        ]
    }


def fake_delete_composednode_ok():
    return {}


def fake_delete_composednode_fail():
    return {
        "error": {
            "code": "Base.1.0.UnknownException",
            "message": "The specified node could not be disassembled",
            "@Message.ExtendedInfo": [{
                "Message": "Disassembly failed: Could not power off composed "
                           "node: ComputerSystem 33 reset action"
                           "(GracefulShutdown) failed"
            }]
        }
    }


def fake_allocate_node_conflict():
    return {
        "error": {
            "code": "Base.1.0.ResourcesStateMismatch",
            "message": "Conflict during allocation",
            "@Message.ExtendedInfo": [{
                "Message": "There are no computer systems available for this "
                           "allocation request."
            }, {
                "Message": "Available assets count after applying filters: ["
                           "available: 0 -> status: 0 -> resource: 0 -> "
                           "chassis: 0 -> processors: 0 -> memory: 0 -> "
                           "local drives: 0 -> ethernet interfaces: 0]"
            }]
        }
    }


def fake_assemble_node_failed():
    return {
        "error": {
            "code": "Base.1.0.InvalidPayload",
            "message": "Request payload is invalid or missing",
            "@Message.ExtendedInfo": [{
                "Message": "Assembly action could not be completed!"
            }, {
                "Message": "Assembly failed: Only composed node in ALLOCATED "
                           "state can be assembled"
            }]
        }
    }


def fake_rack_list():
    return [
        {
            "Description": "Rack created by PODM",
            "Id": "2",
            "Manufacturer": "Intel",
            "Model": "RSD_1",
            "Name": "Rack 1",
            "SerialNumber": "12345",
            "Links": {
                "Contains": [],
                "ComputerSystems": [
                    {"@odata.id": "/redfish/v1/Systems/1"},
                    {"@odata.id": "/redfish/v1/Systems/2"},
                    {"@odata.id": "/redfish/v1/Systems/3"}
                ]
            }
        },
        {
            "Description": "Rack created by PODM",
            "Id": "3",
            "Manufacturer": "Intel",
            "Model": "RSD_1",
            "Name": "Rack 2",
            "SerialNumber": "12346",
            "Links": {
                "Contains": [],
                "ComputerSystems": [
                    {"@odata.id": "/redfish/v1/Systems/4"},
                    {"@odata.id": "/redfish/v1/Systems/5"}
                ]
            }
        }
    ]
