Advanced Topics
===============

Customization
-------------

Parameter names and wildcard values can be configured with the Django setting
``REST_FLEX_FIELDS2``. For the corresponding constants exposed by the package,
see :doc:`/reference/api-reference`.

.. list-table::
   :header-rows: 1
   :widths: 35 45 20

   * - Option
     - Description
     - Default
   * - ``EXPAND_PARAM``
     - Query parameter name for requested expansions.
     - ``"expand"``
   * - ``MAXIMUM_EXPANSION_DEPTH``
     - Maximum allowed expansion depth. ``None`` means unlimited.
     - ``None``
   * - ``FIELDS_PARAM``
     - Query parameter name for sparse field inclusion.
     - ``"fields"``
   * - ``OMIT_PARAM``
     - Query parameter name for explicit exclusions.
     - ``"omit"``
   * - ``RECURSIVE_EXPANSION_PERMITTED``
     - Whether recursive expansion patterns are allowed.
     - ``True``
   * - ``WILDCARD_VALUES``
     - Wildcard values that mean all fields or all expandable fields. Set to
       ``None`` to disable wildcards.
     - ``["*", "~all"]``

Example:

.. code-block:: python

   REST_FLEX_FIELDS2 = {
       "EXPAND_PARAM": "include",
   }

.. warning::

    Avoid direct import of the ``rest_flex_fields2`` package in the Django settings.
    Otherwise the configuration will not be picked up, because the variable does not
    necessarily exist at the time of the import. Always reference package contents
    like class names as strings, instead of importing them.

Defining Limits on Serializer Classes
-------------------------------------

You can set limits directly on a serializer class:

- ``maximum_expansion_depth``
- ``recursive_expansion_permitted``

Both settings raise ``serializers.ValidationError`` when violated. You can
customize the exceptions by overriding ``recursive_expansion_not_permitted()``
and ``expansion_depth_exceeded()``.

Example:

.. code-block:: python

   class PersonSerializer(FlexFieldsModelSerializer):
       maximum_expansion_depth = 2
       recursive_expansion_permitted = False

       class Meta:
           model = Person
           fields = ["id", "name", "manager"]
           expandable_fields = {
               "manager": "people.api.serializers.PersonSerializer",
           }

With this configuration, requests such as ``?expand=manager.manager.manager``
raise a validation error.

Serializer Introspection
------------------------

Instances of ``FlexFieldsModelSerializer`` expose ``expanded_fields``, which
records the fields expanded during serialization.

.. code-block:: python

   serializer = PersonSerializer(
       instance=person,
       context={"request": request},
   )
   payload = serializer.data
   expanded = serializer.expanded_fields

``expanded`` can be used in tests to assert behavior for a specific query.

Wildcards
---------

You can use wildcard values such as ``*`` to expand or include all fields at a
given level.

Examples:

- ``expand=*``
- ``expand=menu.sections``
- ``fields=*,restaurant.name,restaurant.address&expand=restaurant``

Combining Sparse Fields and Expansion
-------------------------------------

Sparse fieldsets take precedence over expansion. If a field is not explicitly
allowed by ``fields``, it will not be expanded even if it appears in ``expand``.

For example, this request omits ``country`` from the response because ``fields``
wins:

.. code-block:: text

   GET /person/13322?fields=id,name&expand=country

Response:

.. code-block:: json

   {
       "id": 13322,
       "name": "John Doe"
   }

Utility Functions
-----------------

For broader endpoint usage patterns that pair with these helpers, see
:doc:`/guide/usage`.

``rest_flex_fields2.is_expanded(request, field)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Returns whether a field was requested via the active expansion parameter.

``rest_flex_fields2.is_included(request, field)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Returns whether a field remains included after ``fields`` and ``omit`` are
applied.

Example view usage:

.. code-block:: python

  from rest_flex_fields2.utils import is_expanded


   class PersonViewSet(FlexFieldsModelViewSet):
       serializer_class = PersonSerializer

       def get_queryset(self):
           queryset = Person.objects.all()

           if is_expanded(self.request, "country"):
               queryset = queryset.select_related("country")

           return queryset

Query Optimization Backend
--------------------------

``FlexFieldsFilterBackend`` is an optional integration that applies queryset
optimization based on requested expansions and sparse fieldsets. You do not
need this backend to use dynamic expansion (``expand``) or sparse fieldsets
(``fields`` and ``omit``). Those core features work through the serializer
layer. But you can add ``FlexFieldsFilterBackend`` when you want automatic
queryset tuning from request parameters to reduce query count and payload
size automatically. It applies ``select_related()``, ``prefetch_related()``,
and ``only()`` based on the requested fields and expansions.

.. code-block:: python

   REST_FRAMEWORK = {
       "DEFAULT_FILTER_BACKENDS": (
           "rest_flex_fields2.filter_backends.FlexFieldsFilterBackend",
       ),
   }

.. warning::

   The optimization currently works for one nesting level only. Treat it as a
   convenience feature, not as a substitute for inspecting your queryset
   behavior.
