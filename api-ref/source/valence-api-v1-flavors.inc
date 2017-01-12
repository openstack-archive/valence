.. -*- rst -*-

============
Flavors
============

List, Searching of Flavors through the ``/v1/flavors``


List Flavors
============

.. rest_method::  GET /v1/flavors/

Normal response codes: 200

Error response codes: badRequest(400), unauthorized(401), forbidden(403)

Request
-------

Response
--------


**Example list of Flavor :**

.. literalinclude:: mockup/flavor-list-response.json
   :language: javascript


Create Flavor
=============

.. rest_method:: POST /v1/flavors

Normal response codes: 200

Error response codes: badRequest(400), unauthorized(401), forbidden(403), 404, 409

Request
-------

.. rest_parameters:: parameters.yaml

    - name: flavor_name
    - ram: flavor_ram
    - processor_model: flavor_processor_model
    - cores: flavor_cores

**Example generate flavor :**

.. literalinclude:: mockup/flavor-post.json
   :language: javascript

Response
---------

**Example list of Flavor :**

.. literalinclude:: mockup/flavor-post-response.json
   :language: javascript

Update Flavor
=============

.. rest_method:: PATCH /v1/flavors/{flavor_uuid}

Updates the information stored about a flavor.

Normal response codes: 200

Error response codes: badRequest(400), unauthorized(401), forbidden(403), 404

Request
-------

.. rest_parameters:: parameters.yaml

   - flavor_uuid: flavor_uuid

Response
--------

.. rest_parameters:: parameters.yaml

   - uuid: flavor_uuid
   - name: flavor_name
   - ram: flavor_ram
   - processor_model: flavor_processor_model
   - cores: flavor_cores

Delete Flavor
=============

.. rest_method:: DELETE /v1/flavors/{flavor_uuid}

Deletes a flavor.

Normal response codes: 204

Error response codes: 401, 403, 404, 409

Request
-------

.. rest_parameters:: parameters.yaml

   - flavor_ident: flavor_ident
