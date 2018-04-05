.. -*- rst -*-

=======
Devices
=======

List, Searching and Sync of devices are done through the ``/v1/devices``

List Devices
============

.. rest_method::  GET /v1/devices/

Return a list of Devices.
Some filtering is possible by passing in filters with the request.
.. NOTE::
    Request format: GET /v1/devices?{filters}
    where filters can be combination of keys: node_id, podm_id, state,
    type, pooled_group_id, resource_uri.
    For example: GET /v1/devices?node_id=0x000000&type=SSD
By default, this query will return all devices with uuid, podm_id,
type, state, node_id, resource_uri and pooled_group_id.

Normal response codes: 200
Error response codes: badRequest(400), unauthorized(401), forbidden(403)

Request
-------

Response
--------

.. rest_parameters:: parameters.yaml

    - node_id: node_index
    - podm_id: podm_uuid
    - pooled_group_id: device_group_id
    - resource_uri: device_uri
    - state: device_state
    - type: device_type
    - uuid: device_uuid

**Example list of Devices:**

.. literalinclude:: mockup/devices-list-response.json
   :language: javascript


Display Device Details
======================

.. rest_method::  GET /v1/devices/{device_id}

Shows details for a Device.
This will return the full representation of the device.

Normal response codes: 200

Error response codes: badRequest(400), unauthorized(401), forbidden(403)

Request
-------

.. rest_parameters:: parameters.yaml

    - id: device_id

Response
--------

.. rest_parameters:: parameters.yaml

    - created_at: created_at
    - extra: device_details
    - node_id: node_index
    - podm_id: podm_uuid
    - pooled_group_id: device_group_id,
    - properties: device_properties
    - resource_uri: device_uri
    - state: device_state
    - type: device_type
    - updated_at: updated_at
    - uuid: device_uuid

**Example JSON representation of a Device:**

.. literalinclude:: mockup/devices-get-response.json
   :language: javascript


Sync Devices
============

.. rest_method::  POST /v1/devices/sync

Sync all devices managed with podmanager.
Synchronization of devices connected to one podmanager is possible by
passing ``podm_id`` in the body of POST request.
By default it will sync devices connected to all podmanagers one by one.

Normal response codes: 200

Error response codes: badRequest(400), unauthorized(401), forbidden(403)

Request
-------

Response
--------

.. rest_parameters:: parameters.yaml

    - podm_id: podm_uuid
    - status: sync_status

**Example JSON representation of a Sync response:**

.. literalinclude:: mockup/devices-sync-response.json
   :language: javascript
