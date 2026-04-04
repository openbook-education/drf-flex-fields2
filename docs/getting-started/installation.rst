Installation
============

``drf-flex-fields2`` is a thin extension for Django REST Framework serializers.
It keeps your existing serializer design and adds three request-driven controls:
``expand`` for nested representations, ``fields`` for sparse inclusion, and
``omit`` for explicit exclusions. For behavior examples, see
:doc:`/guide/usage`.

Install the package from PyPI:

.. code-block:: bash

    pip install drf-flex-fields2

Then subclass ``FlexFieldsModelSerializer`` in place of DRF's regular
``ModelSerializer``:

.. code-block:: python

    from rest_flex_fields2.serializers import FlexFieldsModelSerializer


    class StateSerializer(FlexFieldsModelSerializer):
        class Meta:
            model = State
            fields = ("id", "name")


    class CountrySerializer(FlexFieldsModelSerializer):
        class Meta:
            model = Country
            fields = ("id", "name", "population", "states")
            expandable_fields = {
                "states": (StateSerializer, {"many": True}),
            }

If you already have a custom serializer base class, you can instead mix in
``FlexFieldsSerializerMixin``. See :ref:`using-the-serializer-mixin` for a
practical integration pattern.

Optional Django settings
------------------------

Runtime behavior can be customized with the ``REST_FLEX_FIELDS2`` setting
(see also :doc:`/reference/api-reference` for configuration constants):

.. code-block:: python

    REST_FLEX_FIELDS2 = {
        "EXPAND_PARAM": "expand",
        "FIELDS_PARAM": "fields",
        "OMIT_PARAM": "omit",
    }

The full list of supported settings is documented in :doc:`/guide/advanced`.

Next steps
----------

- Follow :doc:`/getting-started/quickstart` for a complete first
  request/response flow.
- Read :doc:`/getting-started/core-concepts` for the request semantics behind ``expand``,
  ``fields``, and ``omit``.
