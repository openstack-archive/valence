.. -*- rst -*-

================
API versions v1
================

Concepts
========

In order to bring new features to users over time, the Valence API
supports versioning. There are two kinds of versions in Valence.

- ''major versions'', which have dedicated urls.
- ''microversions'', which can be requested through the use of the
  ``OpenStack-API-Version`` header.

The Version APIs work differently from other APIs as they do not require authentication.

All API requests support the ``OpenStack-API-Version`` header.
This header SHALL be supplied with every request.
This help to provide backwards compatibility as we introduced new features in the server.

List API versions
=================

.. rest_method::  GET /

This fetches all the information about all known major API versions in the
deployment. Links to more specific information will be provided for each major
API version, as well as information about supported min and max microversions.

Normal response codes: 200

Request
-------

Response Example
----------------

.. rest_parameters::  parameters.yaml

    - versions: versions
    - id: id
    - links: links
    - max_version: x-openstack-valence-api-max-version
    - min_version: x-openstack-valence-api-min-version

.. literalinclude:: mockup/api-root-response.json
   :language: javascript


Show v1 API
===========

.. rest_method::  GET /v1/

Show all the resources within the Valence v1 API.

Normal response codes: 200

Request
-------

Response Example
----------------

.. rest_parameters::  parameters.yaml

    - id: id
    - links: links
    - openstack-request-id: openstack-request-id

.. literalinclude:: mockup/api-v1-root-response.json
   :language: javascript
