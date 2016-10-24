.. -*- rst -*-

============
Flavors
============

List, Searching of Flavors through the ``/v1/flavor``


List Flavor 
============

.. rest_method::  GET /v1/flavor/


Leaving this empty for discussion due to there isn't a DB to keep generated flavor.

Normal response codes: 200

Error response codes: badRequest(400), unauthorized(401), forbidden(403)

Request
-------

Response
--------


**Example list of Flavor :**

.. literalinclude:: mockup/flavor-list-response.json
   :language: javascript


Generate Flavor
=============== 

.. rest_method:: POST /v1/flavor

Normal response codes: 200

Error response codes: badRequest(400), unauthorized(401), forbidden(403), 404, 409

Request
-------

.. rest_parameters:: parameters.yaml

    - criterial: criteria_list 

**Example generate flavor :**

.. literalinclude:: mockup/flavor-post.json
   :language: javascript

Response
---------

**Example list of Flavor :**

.. literalinclude:: mockup/flavor-post-response.json
   :language: javascript

List Flavor criteria
=====================

.. rest_method::  GET /v1/flavor/criteria

Get all supported flavor generation criteria along with their description.

Normal response codes: 200

Error response codes: unauthorized(401), forbidden(403)

Request
-------


Response
--------

.. rest_parameters:: parameters.yaml

    - criteria: criteria_object 

**Example JSON representation of a Compute System:**

.. literalinclude:: mockup/flavor-criteria-get-response.json
   :language: javascript

