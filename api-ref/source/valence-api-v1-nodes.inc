.. -*- rst -*-

==================
Composed nodes 
==================

List, Searching, Creating, Updating, and Deleting of Composed Node resources
are done through the ``/v1/nodes`` resource. 

A Composed node may be referenced both by its UUID and by a unique "name".
Send feedback to Valence team or [chester.kuo@gmail.com]

Create Node
===========

.. rest_method::  POST /v1/nodes

Creates a new Composed node with specific resources or empty request in json request
file.

Normal response codes: 200

Error response codes: badRequest(400), unauthorized(401), forbidden(403)

Request
-------

.. rest_parameters:: parameters.yaml

   - name: node_request_name
   - description: node_request_description

**Example Node creation request:**

.. literalinclude:: mockup/composed-node-create-request.json
   :language: javascript

Response
--------

The response will contain the complete node uuid and name record

The list and example below are representative of the response as of API 

.. rest_parameters:: parameters.yaml

    - uuid: node_uuid
    - name: node_name
    - links: links

**Example JSON representation of a Node:**

.. literalinclude:: mockup/composed-node-create-response.json
   :language: javascript


List Nodes
==========

.. rest_method::  GET /v1/nodes

Return a list of Composed nodes.
some filtering is possible by passing in flags with the request.

By default, this query will return node object with the name, uuid and node_state 

Normal response codes: 200

Error response codes: badRequest(400), unauthorized(401), forbidden(403)

Request
-------

Response
--------

.. rest_parameters:: parameters.yaml

    - uuid: node_uuid
    - name: node_name
    - node_state: node_state
    - links: links

**Example list of composed nodes:**

.. literalinclude:: mockup/composed-nodes-list-response.json
   :language: javascript


List Composed node Details
=============================

.. rest_method::  GET /v1/nodes/{node-ident}

Shows details for a composed node.
This will return the full representation of the resources

Normal response codes: 200

Error response codes: badRequest(400), unauthorized(401), forbidden(403)

Request
-------

.. rest_parameters:: parameters.yaml

    - node_ident: node_ident
    - fields: fields

Response
--------

.. rest_parameters:: parameters.yaml

    - uuid: node_uuid
    - description: node_description
    - name: node_name
    - node_state: node_state
    - metadata: node_metadata
    - boot_source: node_boot_source
    - pooled_group_id: pooled_group_id
    - health_status: node_health_status
    - chassis_id : node_chassis_id
    - node_property: node_property
    - created_at: created_at 
    - updated_at: updated_at 
    - provision_state: node_provision_state
    - links: links

**Example JSON representation of a Node:**

.. literalinclude:: mockup/composed-node-get-response.json
   :language: javascript


Update Node
===========

.. rest_method::  PATCH /v1/nodes/{node_ident}

Updates the property stored about a composed node.

Note that this endpoint can not be used to request state changes, which are
managed through sub-resources.

Normal response codes: 200

Error response codes: badRequest(400), unauthorized(401), forbidden(403), 404

Request
-------

The BODY of the PATCH request must be a JSON PATCH document, adhering to
`RFC 6902 <https://tools.ietf.org/html/rfc6902>`_.

.. rest_parameters:: parameters.yaml

   - node_ident: node_ident

**Example PATCH document updating composed node :**

.. literalinclude:: mockup/node-update-name-info-request.json

Response
--------

.. rest_parameters:: parameters.yaml

    - uuid: node_uuid
    - description: node_description
    - name: node_name
    - node_state: node_state
    - metadata: node_metadata
    - boot_source: node_boot_source
    - pooled_group_id: pooled_group_id
    - health_status: node_health_status
    - chassis_id : node_chassis_id
    - node_property: node_property
    - created_at: created_at 
    - updated_at: updated_at
    - provision_state: node_provision_state
    - links: links

**Example JSON representation of a Node:**

.. literalinclude:: mockup/composed-node-get-response.json
   :language: javascript


Delete Node
===========

.. rest_method::  DELETE /v1/nodes/{node_ident}

Deletes a node.

Normal response codes: 204

Error response codes: 401,403, 404 ,409

Request
-------

.. rest_parameters:: parameters.yaml

   - node_ident: node_ident

Response
--------

