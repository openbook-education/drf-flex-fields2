Installation
============

Install the package from PyPI:

.. code-block:: bash

   pip install drf-flex-fields2

Then subclass ``FlexFieldsModelSerializer`` in place of DRF's regular
``ModelSerializer``:

.. code-block:: python

   from rest_flex_fields2 import FlexFieldsModelSerializer


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
``FlexFieldsSerializerMixin``.

Optional Django settings
------------------------

Runtime behavior can be customized with the ``REST_FLEX_FIELDS`` setting:

.. code-block:: python

   REST_FLEX_FIELDS = {
       "EXPAND_PARAM": "expand",
       "FIELDS_PARAM": "fields",
       "OMIT_PARAM": "omit",
   }

The full list of supported settings is documented in :doc:`advanced`.
