from valence.db import models


def fake_device():
    return {
        "created_at": "2018-01-18 10:36:29 UTC",
        "extra": {
            "device_name": "Qwerty device",
            "vendor_name": "Qwerty Technologies"
        },
        "node_id": None,
        "podm_id": "88888888-8888-8888-8888-888888888888",
        "pooled_group_id": "0000",
        "properties": {
            "device_id": "0x7777777777",
            "mac_address": "77:77:77:77:77:77"
        },
        "resource_uri": "devices/0x7777777777",
        "state": "free",
        "type": "NIC",
        "updated_at": "2018-01-23 05:46:32 UTC",
        "uuid": "00000000-0000-0000-0000-000000000000"
    }


def fake_device_obj():
    return models.Device(**fake_device())


def fake_device_list():
    return [
        {
            "node_id": "0x11111111111",
            "podm_id": "wwwwwwww-wwww-wwww-wwww-wwwwwwwwwwwwwwww",
            "pooled_group_id": "1111",
            "resource_uri": "devices/0x22222222222",
            "state": "allocated",
            "type": "NIC",
            "uuid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        },
        {
            "node_id": None,
            "podm_id": "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy",
            "pooled_group_id": "0000",
            "resource_uri": "devices/0x666666666666",
            "state": "free",
            "type": "NIC",
            "uuid": "zzzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzz"
        }
        ]


def fake_device_obj_list():
    values_list = fake_device_list()
    for i in range(len(values_list)):
        values_list[i] = models.Device(**values_list[i])

    return values_list
