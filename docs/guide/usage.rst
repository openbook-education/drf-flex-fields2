Usage
=====

This page focuses on day-to-day endpoint behavior. For setting-level controls,
see :doc:`/guide/advanced`. For option syntax and constructor-time usage, see
:doc:`/guide/serializer-options`.

Dynamic Field Expansion
-----------------------

To define expandable fields, add an ``expandable_fields`` dictionary to the
serializer's ``Meta`` class. Each key is the field name to expand dynamically.
Each value is either a serializer class or a tuple of serializer class plus
serializer keyword arguments. Related option combinations are documented in
:doc:`/guide/serializer-options`.

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

.. code-block:: python

   class TeamSerializer(FlexFieldsModelSerializer):
       class Meta:
           model = Team
           fields = ["id", "name"]


   class MemberSerializer(FlexFieldsModelSerializer):
       class Meta:
           model = Member
           fields = ["id", "email"]
           expandable_fields = {
               "team": TeamSerializer,
           }

Default response for ``GET /members/87/``:

.. code-block:: json

   {
       "id": 87,
       "email": "sam@example.com"
   }

Expanded response for ``GET /members/87/?expand=team``:

.. code-block:: json

   {
       "id": 87,
       "email": "sam@example.com",
       "team": {
           "id": 11,
           "name": "API Platform"
       }
   }

Deep Nested Expansion
---------------------

This example demonstrates a two-level expansion: first ``country`` on
``PersonSerializer``, then ``states`` on ``CountrySerializer``. The resulting
request ``expand=country.states`` returns a person payload with nested country
and state details.

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
               # Expand states only when the client asks for them.
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

.. warning::

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

Lazy Serializer References
--------------------------

To avoid circular imports, reference a serializer lazily by dotted path:

.. code-block:: python

   class OwnerSerializer(FlexFieldsModelSerializer):
       class Meta:
           model = Owner
           fields = ["id", "name"]


   class RecordSerializer(FlexFieldsModelSerializer):
       class Meta:
           model = Record
           fields = ["id", "title", "owner"]
           expandable_fields = {
               "owner": "accounts.api.serializers.UserSerializer",
               "record_set": (
                   "records.api.serializers.RelatedSerializer",
                   {"many": True},
               ),
           }

Fully qualified import paths are supported. Legacy
``<app>.serializers.SerializerName`` paths still work as well.

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

