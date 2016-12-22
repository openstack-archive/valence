.. -*- rst -*-

====
Rack
====

List, Searching of hardware racks through the ``/v1/racks`` resource.

List Racks
==========

.. rest_method::  GET /v1/racks/

Return a list of Racks.
Some filtering is possible by passing in flags with the request.
By default, this query will return racks with id, name, location and
contained compute systems.

Normal response codes: 200
Error response codes: badRequest(400), unauthorized(401), forbidden(403)

Request
-------

Response
--------

.. rest_parameters:: parameters.yaml

    - id: rack_id
    - name: rack_name
    - systems: rack_systems

**Example list of Racks:**

.. literalinclude:: mockup/rack-list-response.json
   :language: javascript


Display Rack Details
====================

.. rest_method::  GET /v1/racks/{rack_id}

Shows details for a Rack.
This will return the full representation of the resources.

Normal response codes: 200

Error response codes: badRequest(400), unauthorized(401), forbidden(403)

Request
-------

.. rest_parameters:: parameters.yaml

    - id: rack_id

Response
--------

.. rest_parameters:: parameters.yaml

    - id: rack_id
    - name: rack_name
    - systems: rack_systems
    - manufacturer: rack_manufacturer
    - model: rack_model
    - description: rack_description
    - serial_number: rack_serial_number

**Example JSON representation of a Rack:**

.. literalinclude:: mockup/rack-get-response.json
   :language: javascript