from common import AuthResource


class Redfishv1Resource(AuthResource):
    def get(self):
        return {
            "@odata.context": "/redfish/v1/$metadata#ServiceRoot.ServiceRoot",
            "@odata.id": "/redfish/v1/",
            "@odata.type": "#ServiceRoot.1.0.0.ServiceRoot",
            "Id": "RootService",
            "Name": "Root Service",
            "RedfishVersion": "1.0.0",
            "UUID": "92384634-2938-2342-8820-489239905423",
            "Systems": {"@odata.id": "/redfish/v1/Systems"
                        },
            "Chassis": {
                "@odata.id": "/redfish/v1/Chassis"
            },
            "Managers": {
                "@odata.id": "/redfish/v1/Managers"
            },
            "EventService": {
                "@odata.id": "/redfish/v1/EventService"
            },
            "Services": {
                "@odata.id": "/redfish/v1/Services"
            },
            "Nodes": {
                "@odata.id": "/redfish/v1/Nodes"
            },
            "EthernetSwitches": {
                "@odata.id": "/redfish/v1/EthernetSwitches"
            },
            "Oem": {
                "Intel:RackScale": {
                    "@odata.type": "#Intel.Oem.ServiceRoot",
                    "ApiVersion": "1.2.0",
                }
            },
            "Links": {}
        }
