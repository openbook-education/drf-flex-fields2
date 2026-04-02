Core Concepts
=============

``drf-flex-fields2`` extends DRF serializer output using request parameters.
The behavior is intentionally explicit so API clients can control payload size
without requiring many serializer variants.

Request parameters
------------------

- ``expand``: Replace relation identifiers with nested serializer output.
- ``fields``: Keep only explicitly selected fields.
- ``omit``: Remove explicitly excluded fields.

Conceptually, the output shape is computed as:

1. Start with serializer defaults.
2. Apply ``fields`` if present.
3. Apply ``omit``.
4. Expand remaining expandable fields from ``expand``.

Because sparse selection is applied before expansion, ``fields`` can prevent an
otherwise valid expansion from appearing in the response.

Dot notation
------------

Nested paths use dot notation in all three parameters.

Examples:

- ``expand=country.states``
- ``fields=id,name,country.name``
- ``omit=country.population``

Wildcards
---------

By default, ``*`` and ``~all`` can be used as wildcard values.

Examples:

- ``expand=*`` expands all expandable fields at the current level.
- ``fields=*`` includes all serializer fields.

These values are configurable through ``REST_FLEX_FIELDS2``.

Example Requests
----------------

Use either ``fields`` or ``omit`` to control the output shape.

Default response:

.. code-block:: json

   {
       "id": 13322,
       "name": "John Doe",
       "country": {
           "name": "United States",
           "population": 330000000
       },
       "occupation": "Programmer",
       "hobbies": ["rock climbing", "sipping coffee"]
   }

Request with ``?fields=id,name,country``:

.. code-block:: json

   {
       "id": 13322,
       "name": "John Doe",
       "country": {
           "name": "United States",
           "population": 330000000
       }
   }

Request with ``?fields=id,name,country.name``:

.. code-block:: json

   {
       "id": 13322,
       "name": "John Doe",
       "country": {
           "name": "United States"
       }
   }

Request with ``?omit=country``:

.. code-block:: json

   {
       "id": 13322,
       "name": "John Doe",
       "occupation": "Programmer",
       "hobbies": ["rock climbing", "sipping coffee"]
   }


Where to apply controls
-----------------------

- Serializer-level: default behavior and expandable field declarations.
- View-level: list-action restrictions and queryset optimization.
- Project-level: parameter names and wildcard/depth settings.

Continue with :doc:`/guide/usage` for practical endpoint patterns and
:doc:`/guide/advanced` for settings, limits, and optimization behavior.
