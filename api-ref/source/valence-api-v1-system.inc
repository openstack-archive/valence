.. -*- rst -*-

==============
Compute System
==============

List, Searching of Composed Node resources are done through the ``/v1/systems``

A Compute node may be referenced both by its UUID and by a unique "name".
Send feedback to Valence team or [chester.kuo@gmail.com]

List Compute System
===================

.. rest_method::  GET /v1/systems/

Return a list of Compute System.
some filtering is possible by passing in flags with the request.
By default, this query will return compute system object with the name, uuid and power_state

Normal response codes: 200
Error response codes: badRequest(400), unauthorized(401), forbidden(403)

Request
-------

Response
--------

.. rest_parameters:: parameters.yaml

    - uuid: system_uuid
    - name: system_name
    - power_state: system_power_state
    - links: links

**Example list of Compute System:**

.. literalinclude:: mockup/compute-systems-list-response.json
   :language: javascript


List Compute System Details
===========================

.. rest_method::  GET /v1/systems/{system_ident}

Shows details for a Compute System.
This will return the full representation of the resources

Normal response codes: 200

Error response codes: badRequest(400), unauthorized(401), forbidden(403)

Request
-------

.. rest_parameters:: parameters.yaml

    - system_ident: system_ident
    - fields: fields

Response
--------

.. rest_parameters:: parameters.yaml

    - uuid: system_uuid
    - description: node_description
    - name: system_name
    - power_state: system_power_state
    - health: system_health
    - chassis_id : system_chassis_id
    - assettag: system_assettag
    - url_id : system_url_id
    - created_at: created_at
    - updated_at: updated_at
    - links: links

**Example JSON representation of a Compute System:**

.. literalinclude:: mockup/compute-system-get-response.json
   :language: javascript


List Compute System Inventory Details
=====================================

.. rest_method::  GET /v1/systems/{system_ident}/inventory

Shows inventory data for a Compute System.
This will return the full representation of the resources include processor
memory, storage objects

Normal response codes: 200

Error response codes: badRequest(400), unauthorized(401), forbidden(403)

Request
-------

.. rest_parameters:: parameters.yaml

    - system_ident: system_ident

Response
--------

.. rest_parameters:: parameters.yaml

    - processor: system_processor_object
    - memory: system_memory_object
    - storage: system_storage_object
    - network: system_network_object


**Example JSON representation of a Node:**

.. literalinclude:: mockup/compute-system-inventory-get-response.json
   :language: javascript
