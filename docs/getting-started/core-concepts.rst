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

These values are configurable through ``REST_FLEX_FIELDS``.

Where to apply controls
-----------------------

- Serializer-level: default behavior and expandable field declarations.
- View-level: list-action restrictions and queryset optimization.
- Project-level: parameter names and wildcard/depth settings.

Continue with :doc:`/guide/usage` for practical endpoint patterns and
:doc:`/guide/advanced` for settings, limits, and optimization behavior.
