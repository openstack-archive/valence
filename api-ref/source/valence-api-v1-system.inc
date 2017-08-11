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

    - identity: system_identity
    - name: system_name
    - power_state: system_power_state

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

    - asset_tag: system_asset_tag
    - bios_version: system_bios_version
    - boot_enabled: system_boot_enabled
    - boot_mode: system_boot_mode
    - boot_target: system_boot_target
    - description: system_description
    - hostname: system_hostname
    - identity: system_identity
    - indicator_led: system_indicator_led
    - manufacturer: system_manufacturer
    - name: system_name
    - part_number: system_part_number
    - power_state: system_power_state
    - serial_number: system_serial_number
    - sku: system_sku
    - memory_health: system_memory_health
    - memory_size_gib: system_memory_size_gib
    - processor_count: system_processor_count
    - processor_architecture: system_processor_architecture

**Example JSON representation of a Compute System:**

.. literalinclude:: mockup/compute-system-get-response.json
   :language: javascript
