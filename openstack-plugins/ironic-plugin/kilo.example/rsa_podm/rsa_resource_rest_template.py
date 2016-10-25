chassis = {
    "@odata.context": "",
    "@odata.id": "",
    "@odata.type": "",
    "Id": "",
    "ChassisType": "",
    "Name": "",
    "Description": "",
    "Manufacturer": "",
    "Model": "",
    "SKU": "",
    "SerialNumber": "",
    "PartNumber": "",
    "AssetTag": "",
    "IndicatorLED": "",
    "Status": {
        "State": "",
        "Health": "",
        "HealthRollup": ""
    },
    "Oem": {
        "Intel:RackScale": {
            "@odata.type": "",
            "Location": {
                "Id": "",
                "ParentId": ""
            }
        }
    },
    "Links": {
        "Contains": [
            {
                "@odata.id": ""
            }
        ],
        "ContainedBy": {
            "@odata.id": ""
        },
        "ComputerSystems": [

        ],
        "Switches": "",
        "ManagedBy": [
            {
                "@odata.id": ""
            }
        ],
        "ManagersIn": [
            {

            }
        ],
        "Oem": ""
    }
}

computer_system = {
    "@odata.context": "",
    "@odata.id": "",
    "@odata.type": "",
    "Id": "",
    "Name": "",
    "SystemType": "",
    "AssetTag": "",
    "Manufacturer": "",
    "Model": "",
    "SKU": "",
    "SerialNumber": "",
    "PartNumber": "",
    "Description": "",
    "UUID": "",
    "HostName": "",
    "Status": {
        "State": "",
        "Health": "",
        "HealthRollUp": ""
    },
    "IndicatorLED": "",
    "PowerState": "",
    "Boot": {
        "BootSourceOverrideEnabled": "",
        "BootSourceOverrideTarget": "",
        "BootSourceOverrideTarget@Redfish.AllowableValues": []
    },
    "BiosVersion": "",
    "ProcessorSummary": {
        "Count": "",
        "Model": "",
        "Status": {
            "State": "",
            "Health": "",
            "HealthRollUp": ""
        }
    },
    "MemorySummary": {
        "TotalSystemMemoryGiB": "",
        "Status": {
            "State": "",
            "Health": "",
            "HealthRollUp": ""
        }
    },
    "Processors": {
        "@odata.id": ""
    },
    "EthernetInterfaces": {
        "@odata.id": ""
    },
    "SimpleStorage": {},
    "DimmConfig": {
        "@odata.id": ""
    },
    "MemoryChunks": {
        "@odata.id": ""
    },
    "Links": {
        "Chassis": [
            {
                "@odata.id": ""
            }
        ],
        "ManagedBy": [
            {}
        ],
        "Oem": ""
    },
    "Actions": {
        "#ComputerSystem.Reset": {
            "target": "",
            "ResetType@Redfish.AllowableValues": []
        },
        "Oem": {
            "Intel:RackScale": {
                "#ComputerSystem.StartDeepDiscovery": {
                    "target": ""
                }
            }
        }
    },
    "Oem": {
        "Intel:RackScale": {
            "@odata.type": "",
            "Adapters": {
                "@odata.id": ""
            },
            "PciDevices": [
                {
                    "VendorId": "",
                    "DeviceId": ""
                }
            ],
            "DiscoveryState": "",
            "ProcessorSockets": "",
            "MemorySockets": ""
        }
    }
}

processors = {
    "@odata.context": "",
    "@odata.id": "",
    "@odata.type": "",
    "Name": "",
    "Id": "",
    "Socket": "",
    "ProcessorType": "",
    "ProcessorArchitecture": "",
    "InstructionSet": "",
    "Manufacturer": "",
    "Model": "",
    "ProcessorId": {
        "VendorId": "",
        "IdentificationRegisters": "",
        "EffectiveFamily": "",
        "EffectiveModel": "",
        "Step": "",
        "MicrocodeInfo": ""
    },
    "MaxSpeedMHz": "",
    "TotalCores": "",
    "TotalThreads": "",
    "Status": {
        "State": "",
        "Health": "",
        "HealthRollup": ""
    },
    "Oem": {
        "Intel:RackScale": {
            "@odata.type": "",
            "Brand": "",
            "Capabilities": [

            ],
            "ContainedBy": {

            }
        }
    }
}

memory_dimm = {
    "@odata.context": "",
    "@odata.id": "",
    "@odata.type": "",
    "Name": "",
    "Id": "",
    "DimmType": "",
    "DimmDeviceType": "",
    "BaseModuleType": "",
    "DimmMedia": [],
    "CapacityMiB": "",
    "DataWidthBits": "",
    "BusWidthBits": "",
    "Manufacturer": "",
    "SerialNumber": "",
    "PartNumber": "",
    "AllowedSpeedsMHz": [],
    "FirmwareRevision": "",
    "FirmwareApiVersion": "",
    "FunctionClasses": [],
    "VendorId": "",
    "DeviceId": "",
    "RankCount": "",
    "DeviceLocator": "",
    "DimmLocation": {
        "Socket": "",
        "MemoryController": "",
        "Channel": "",
        "Slot": ""
    },
    "ErrorCorrection": "",
    "Status": {
        "State": "",
        "Health": "",
        "HealthRollup": ""
    },
    "OperatingSpeedMHz": "",
    "Regions": [
        {
            "RegionId": "",
            "MemoryType": "",
            "OffsetMiB": "",
            "SizeMiB": ""
        }
    ],
    "OperatingMemoryModes": [
        ""
    ],
    "Oem": {
        "Intel:RackScale": {
            "@odata.type": "",
            "VoltageVolt": ""
        }
    }
}

disk = {
    "@odata.context": "",
    "@odata.id": "",
    "@odata.type": "",
    "Id": "",
    "Name": "",
    "Interface": "",
    "CapacityGiB": "",
    "Type": "",
    "RPM": "",
    "Manufacturer": "",
    "Model": "",
    "SerialNumber": "",
    "FirmwareVersion": "",
    "BusInfo": "",
    "Status": {
        "State": "",
        "Health": "",
        "HealthRollup": ""
    },
    "Oem": {},
    "Links": {
        "ContainedBy": {
            "@odata.id": ""
        },
        "Oem": {}
    }
}

composed_node = {
    "@odata.context": "",
    "@odata.id": "",
    "@odata.type": "",
    "Id": "",
    "Name": "",
    "Description": "",
    "SystemType": "",
    "AssetTag": "",
    "Manufacturer": "",
    "Model": "",
    "SKU": "",
    "SerialNumber": "",
    "PartNumber": "",
    "UUID": "",
    "HostName": "",
    "PowerState": "",
    "BiosVersion": "",
    "Status": {
        "State": "",
        "Health": "",
        "HealthRollUp": ""
    },
    "Processors": {
        "Count": "",
        "Model": "",
        "Status": {
            "State": "",
            "Health": ""
        }
    },
    "Memory": {
        "TotalSystemMemoryGiB": "",
        "Status": {
            "State": "",
            "Health": ""
        }
    },
    "ComposedNodeState": "",
    "Boot": {
        "BootSourceOverrideEnabled": "",
        "BootSourceOverrideTarget": "",
        "BootSourceOverrideTarget@Redfish.AllowableValues": []
    },
    "Oem": {},
    "Links": {
        "ComputerSystem": {
            "@odata.id": ""
        },
        "Processors": [
            {
                "@odata.id": ""
            }
        ],
        "Memory": [
            {
                "@odata.id": ""
            }
        ],
        "EthernetInterfaces": [
            {
                "@odata.id": ""
            }
        ],
        "LocalDrives": [
            {
                "@odata.id": ""
            }
        ],
        "RemoteDrives": [
            {
                "@odata.id": ""
            }
        ],
        "ManagedBy": [
            {
                "@odata.id": ""
            }
        ],
        "Oem": ""
    },
    "Actions": {
        "#ComposedNode.Reset": {
            "target": "",
            "ResetType@Redfish.AllowableValues": []
        },
        "#ComposedNode.Assemble": {
            "target": ""
        }
    }
}

volume = {
    "@odata.context": "",
    "@odata.id": "",
    "@odata.type": "",
    "Id": "",
    "Name": "",
    "Description": "",
    "Status": {
        "State": "",
        "Health": ""
    },
    "Type": "",
    "Mode": "",
    "Protected": "",
    "CapacityGiB": "",
    "Image": "",
    "Bootable": "",
    "Snapshot": "",
    "Oem": {},
    "Links": {
        "LogicalDrives": [],
        "PhysicalDrives": [
            {}
        ],
        "MasterDrive": {},
        "UsedBy": [
            {}
        ],
        "Targets": [
            {}
        ],
        "Oem": {
            "pod": "",
            "Rack": "",
            "ULocation": ""
        }
    }
}

manager = {
    "@odata.context": "",
    "@odata.id": "",
    "@odata.type": "",
    "CommandShell": {
        "ConnectTypesSupported": [],
        "MaxConcurrentSessions": "",
        "ServiceEnabled": ""
    },
    "DateTime": "",
    "DateTimeLocalOffset": "",
    "Description": "",
    "EthernetInterfaces": {
        "@odata.id": ""
    },
    "FirmwareVersion": "",
    "GraphicalConsole": {
        "ConnectTypesSupported": [],
        "MaxConcurrentSessions": "",
        "ServiceEnabled": ""
    },
    "Id": "",
    "Links": {
        "ManagerForChassis": [],
        "ManagerForServers": [],
        "ManagerForSwitches": [],
        "ManagerLocation": {
            "@odata.id": ""
        },
        "Oem": {
            "Intel:RackScale": {
                "@odata.type": "",
                "ManagerForServices": [
                    {
                        "@odata.id": ""
                    }
                ]
            }
        }
    },
    "ManagerType": "",
    "Model": "",
    "Name": "",
    "NetworkProtocol": {
        "@odata.id": ""
    },
    "Oem": {},
    "SerialConsole": {
        "ConnectTypesSupported": [],
        "MaxConcurrentSessions": "",
        "ServiceEnabled": ""
    },
    "ServiceEntryPointUUID": "",
    "Status": {
        "Health": "",
        "State": ""
    },
    "UUID": ""
}
