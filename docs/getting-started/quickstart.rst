Quick Start
===========

This example shows a serializer that exposes a country relation by primary key
unless the client explicitly asks for an expanded nested representation.

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


    class PersonSerializer(FlexFieldsModelSerializer):
        class Meta:
            model = Person
            fields = ("id", "name", "country", "occupation")
            expandable_fields = {
                "country": CountrySerializer,
            }

Default response:

.. code-block:: text

    GET /people/142/

.. code-block:: json

    {
        "id": 142,
        "name": "Jim Halpert",
        "country": 1
    }

Expanded response:

.. code-block:: text

    GET /people/142/?expand=country.states

.. code-block:: json

    {
        "id": 142,
        "name": "Jim Halpert",
        "country": {
            "id": 1,
            "name": "United States",
            "states": [
                {
                    "id": 23,
                    "name": "Ohio"
                },
                {
                    "id": 2,
                    "name": "Pennsylvania"
                }
            ]
        }
    }

From there, continue with :doc:`/guide/usage` for nested expansion, sparse
fieldsets, list-view restrictions, and lazy serializer references. Then use
:doc:`/guide/serializer-options` for constructor and nested serializer option
patterns.

If you are new to the request model, read
:doc:`/getting-started/core-concepts` first and then return to
:doc:`/guide/usage`. For project-level settings and queryset optimization, see
:doc:`/guide/advanced`.
