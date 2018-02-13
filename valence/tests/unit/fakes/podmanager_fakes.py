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

from valence.db import models


def fake_podmanager():
    return {
        "name": "fake-podm",
        "podm_id": "fake-id",
        "url": "https://10.240.212.123",
        "driver": "redfishv1",
        "authentication": [
            {
                "type": "basic",
                "auth_items": {
                    "username": "fake-user",
                    "password": "fake-pass"
                }
            }]
    }


def fake_podm_object():
    return models.PodManager(**fake_podmanager())


def fake_podmanager_list():
    return [
        {
            "authentication": [
                {
                    "auth_items": {
                        "password": "***",
                        "username": "admin"
                    },
                    "type": "basic"
                }],
            "created_at": "2018-02-21 09:40:41 UTC",
            "driver": "redfishv1",
            "name": "podm1",
            "status": "Online",
            "updated_at": "2018-02-21 09:40:41 UTC",
            "url": "http://127.0.0.1:0101",
            "uuid": "0e7957c3-a28a-442d-b61c-0dd0dcb228d7"
        },
        {
            "authentication": [
                {
                    "auth_items": {
                        "password": "***",
                        "username": "admin"
                    },
                    "type": "basic"
                }],
            "created_at": "2018-02-21 09:40:41 UTC",
            "driver": "redfishv1",
            "name": "podm2",
            "status": "Online",
            "updated_at": "2018-02-21 09:40:41 UTC",
            "url": "http://127.0.0.1:0000",
            "uuid": "0e7957c3-a28a-442d-b61c-0dd0dcb228d6"
        }]
