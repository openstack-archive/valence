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
        "error" : {
            "code": "Base.1.0.UnknownException",
            "message": "The specified node could not be disassembled",
            "@Message.ExtendedInfo": [{
                "Message": "Disassembly failed: Could not power off composed "
                           "node: ComputerSystem 33 reset action"
                           "(GracefulShutdown) failed"
            }]
        }
    }
