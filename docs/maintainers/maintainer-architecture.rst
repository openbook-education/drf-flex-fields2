Architecture and Design
=======================

This page explains how the package works beyond the API surface and why the
current module split exists.

Design goals
------------

- Keep serializer APIs close to native DRF behavior.
- Make output-shape control request-driven and explicit.
- Allow opt-in queryset optimization without hidden magic.

Module responsibilities
-----------------------

``serializers.py``
   Implements expansion, sparse fieldsets, and nested option propagation via
   ``FlexFieldsSerializerMixin`` and ``FlexFieldsModelSerializer``.

``views.py``
   Provides ``FlexFieldsMixin`` and ``FlexFieldsModelViewSet`` to control list
   action expansion and pass serializer context constraints.

``filter_backends.py``
   Provides ``FlexFieldsFilterBackend`` for queryset optimization and
   ``FlexFieldsDocsFilterBackend`` for schema parameter support.

``config.py``
   Centralizes runtime settings from ``REST_FLEX_FIELDS`` and exports constants
   used by serializers and utilities.

``utils.py``
   Contains helper logic for parsing nested field paths and checking inclusion
   and expansion intent.

Serialization flow
------------------

1. Root serializer reads request parameters (or constructor kwargs).
2. Sparse field controls are resolved.
3. Expansion paths are validated for recursion and depth.
4. Nested serializers are constructed with propagated options.
5. Output payload is returned using resolved fields and expansions.

Key implementation choices
--------------------------

- Mixin-first design supports custom serializer base classes.
- Lazy serializer references support circular import scenarios.
- Expansion limits and recursive policies are configurable globally and per
  serializer class.
- Query optimization is optional and intentionally conservative.

Extension points
----------------

- Customize query parameter names in ``REST_FLEX_FIELDS``.
- Override serializer validation hooks for expansion policy errors.
- Restrict list expansions with ``permit_list_expands`` on viewsets.
- Pair expansion rules with explicit ``select_related`` and
  ``prefetch_related`` for predictable performance.

When changing internals
-----------------------

1. Add tests for nested expansion and sparse field interactions.
2. Update user documentation if behavior changes.
3. Update this page if module responsibilities or flow changes.
