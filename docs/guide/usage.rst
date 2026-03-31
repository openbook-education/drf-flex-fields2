Usage
=====

This page focuses on day-to-day endpoint behavior. For setting-level controls,
see :doc:`/guide/advanced`.

Dynamic Field Expansion
-----------------------

To define expandable fields, add an ``expandable_fields`` dictionary to the
serializer's ``Meta`` class. Each key is the field name to expand dynamically.
Each value is either a serializer class or a tuple of serializer class plus
serializer keyword arguments.

.. code-block:: python

   class CountrySerializer(FlexFieldsModelSerializer):
       class Meta:
           model = Country
           fields = ["name", "population"]


   class PersonSerializer(FlexFieldsModelSerializer):
       country = serializers.PrimaryKeyRelatedField(read_only=True)

       class Meta:
           model = Person
           fields = ["id", "name", "country", "occupation"]
           expandable_fields = {
               "country": CountrySerializer,
           }

Default response:

.. code-block:: json

   {
       "id": 13322,
       "name": "John Doe",
       "country": 12,
       "occupation": "Programmer"
   }

Expanded response for ``GET /person/13322?expand=country``:

.. code-block:: json

   {
       "id": 13322,
       "name": "John Doe",
       "country": {
           "name": "United States",
           "population": 330000000
       },
       "occupation": "Programmer"
   }

Deferred Fields
---------------

You can treat a relation as deferred by omitting it from the default field list
and defining it only in ``expandable_fields``. The field then appears only when
explicitly expanded.

Deep Nested Expansion
---------------------

Nested expansions use dot notation:

.. code-block:: python

   class StateSerializer(FlexFieldsModelSerializer):
       class Meta:
           model = State
           fields = ["name", "population"]


   class CountrySerializer(FlexFieldsModelSerializer):
       class Meta:
           model = Country
           fields = ["name", "population"]
           expandable_fields = {
               "states": (StateSerializer, {"many": True}),
           }


   class PersonSerializer(FlexFieldsModelSerializer):
       country = serializers.PrimaryKeyRelatedField(read_only=True)

       class Meta:
           model = Person
           fields = ["id", "name", "country", "occupation"]
           expandable_fields = {
               "country": CountrySerializer,
           }

Request:

.. code-block:: text

   GET /person/13322?expand=country.states

Response:

.. code-block:: json

   {
       "id": 13322,
       "name": "John Doe",
       "occupation": "Programmer",
       "country": {
           "id": 12,
           "name": "United States",
           "states": [
               {
                   "name": "Ohio",
                   "population": 11000000
               }
           ]
       }
   }

Be deliberate with nested expansions on large result sets. They can increase
query count substantially unless you pair them with ``select_related()`` or
``prefetch_related()``.

Expansion on List Views
-----------------------

Subclass ``FlexFieldsModelViewSet`` when you want to limit which fields may be
expanded on list endpoints. This is useful when list endpoints would otherwise
cause expensive relation loading for large result sets.

.. code-block:: python

   from rest_flex_fields2 import FlexFieldsModelViewSet, is_expanded


   class PersonViewSet(FlexFieldsModelViewSet):
       permit_list_expands = ["employer"]
       serializer_class = PersonSerializer

       def get_queryset(self):
           queryset = models.Person.objects.all()

           if is_expanded(self.request, "employer"):
               queryset = queryset.select_related("employer")

           return queryset

``permit_list_expands`` is applied only for the list action. The view passes
the allowed values through ``context["permitted_expands"]`` so the serializer
can reject disallowed list-time expansions while still allowing detail-time
expansions.

Expanding a To-Many Relationship
--------------------------------

Set ``many=True`` in the serializer options when the expanded relation returns
multiple objects.

.. code-block:: python

   class CountrySerializer(FlexFieldsModelSerializer):
       class Meta:
           model = Country
           fields = ["name", "population"]
           expandable_fields = {
               "states": (StateSerializer, {"many": True}),
           }

Sparse Fieldsets
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

Lazy Serializer References
--------------------------

To avoid circular imports, reference a serializer lazily by dotted path:

.. code-block:: python

   expandable_fields = {
       "record_set": ("<module_path_to_serializer_class>.RelatedSerializer", {"many": True}),
   }

Fully qualified import paths are supported. Legacy
``<app>.serializers.SerializerName`` paths still work as well.

Example:

.. code-block:: python

   expandable_fields = {
       "owner": ("accounts.api.serializers.UserSerializer", {"many": False}),
   }

Use lazy references when two serializers would otherwise import each other.

.. _using-the-serializer-mixin:

Using FlexFieldsSerializerMixin with a Custom Base
--------------------------------------------------

If your project already has a custom serializer base class, use
``FlexFieldsSerializerMixin`` directly.

.. code-block:: python

   from rest_framework import serializers

   from rest_flex_fields2 import FlexFieldsSerializerMixin


   class BaseAPISerializer(serializers.ModelSerializer):
       class Meta:
           abstract = True


   class AccountSerializer(FlexFieldsSerializerMixin, BaseAPISerializer):
       class Meta:
           model = Account
           fields = ["id", "name", "owner"]
           expandable_fields = {
               "owner": "accounts.api.serializers.UserSerializer",
           }

Serializer Reuse
----------------

``fields`` and ``omit`` can also be passed directly to nested serializer
instances, which helps avoid maintaining multiple slightly different serializers.

.. code-block:: python

   from rest_flex_fields2 import FlexFieldsModelSerializer


   class CountrySerializer(FlexFieldsModelSerializer):
       class Meta:
           model = Country
           fields = ["id", "name", "population", "capital", "square_miles"]


   class PersonSerializer(FlexFieldsModelSerializer):
       country = CountrySerializer(fields=["id", "name"])

       class Meta:
           model = Person
           fields = ["id", "name", "country"]

Real-World Example: Catalog Endpoint
------------------------------------

An e-commerce catalog can keep list responses light while exposing category
details on demand.

.. code-block:: text

   GET /products/?fields=id,name,price,category&expand=category.parent

.. code-block:: json

   {
       "id": 1001,
       "name": "Trail Backpack",
       "price": "89.00",
       "category": {
           "id": 12,
           "name": "Backpacks",
           "parent": {
               "id": 2,
               "name": "Outdoor"
           }
       }
   }

Real-World Example: SaaS Memberships
------------------------------------

A multi-tenant API can return a compact member list and allow clients to expand
the organization only when needed.

.. code-block:: text

   GET /members/?omit=permissions&expand=organization

.. code-block:: json

   {
       "id": 87,
       "email": "sam@example.com",
       "organization": {
           "id": 11,
           "name": "Acme Corp"
       }
   }
