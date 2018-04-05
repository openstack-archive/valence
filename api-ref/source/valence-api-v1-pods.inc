.. -*- rst -*-

==============
Pod managers
==============

Creating, Listing, searching of Pod Manager resources is done through the
``/v1/pod_managers``
Send feedback to Valence team or [chester.kuo@gmail.com]

Create Pod manager
==================

.. rest_method:: POST /v1/pod_manager

Creates a new Pod Manager with specific URL, name, authentication credentials
and driver(default driver: ``redfishv1``).

Normal response codes: 200

Error response codes: badRequest(400), unauthorized(401), forbidden(403)

Request
-------

.. rest_parameters:: parameters.yaml

   - name: podmanager_name
   - url: pod_conn_url
   - driver: podm_driver
   - authentication: auth_details

**Example Pod Manager creation request:**

.. literalinclude:: mockup/pod-manager-create-request.json
   :language: javascript

Response
--------

The response will contain the complete pod uuid and name record

The list and example below are representative of the response as of API

.. rest_parameters:: parameters.yaml

    - name: podmanager_name
    - url: pod_conn_url
    - driver: podm_driver
    - authentication: auth_details
    - created_at: created_at
    - updated_at: updated_at
    - uuid: pod_uuid

**Example JSON representation of a Pod Manager:**

.. literalinclude:: mockup/pod-manager-create-response.json
   :language: javascript

List Pod Manager
=================

.. rest_method::  GET /v1/pod_managers/

Return a list of Pod Managers.
Some filtering is possible by passing in flags with the request.
By default, this query will return Pod Managers object with the name, status and uuid.

Normal response codes: 200
Error response codes: badRequest(400), unauthorized(401), forbidden(403)

Request
-------

Response
--------

.. rest_parameters:: parameters.yaml

    - uuid: pod_uuid
    - name: pod_name
    - status: pod_status
    - links: links

**Example list of Pod Managers:**

.. literalinclude:: mockup/pod-managers-list-response.json
   :language: javascript


List Pod Manager Details
========================

.. rest_method::  GET /v1/pod_managers/{pod_managers_ident}

Shows details for a Pod Manager.
This will return the full representation of the resources

Normal response codes: 200

Error response codes: badRequest(400), unauthorized(401), forbidden(403)

Request
-------

.. rest_parameters:: parameters.yaml

    - uuid: pod_uuid
    - fields: fields

Response
--------

.. rest_parameters:: parameters.yaml

    - uuid: pod_uuid
    - name: pod_name
    - auth: pod_auth_info
    - status: pod_status
    - description: pod_description
    - location: pod_location_id
    - redfish_link : pod_redfish_link
    - created_at: created_at
    - updated_at: updated_at
    - links: links

**Example JSON representation of a Pod Manager:**

.. literalinclude:: mockup/pod-manager-get-response.json
   :language: javascript


Remove Pod Manager
==================

.. rest_method::  DELETE /v1/pod_managers/{pod_manager_ident}

Remove a Pod manager resource from Valence.

Normal response codes: 204

Error response codes: 401,403, 404 ,409

Request
-------

.. rest_parameters:: parameters.yaml

   - pod_uuid: pod_uuid
