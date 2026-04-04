"""Integration tests for ``FlexFieldsModelSerializer`` serialization behaviour."""

from typing import cast
from unittest.mock import patch

from django.test import TestCase
from django.utils.datastructures import MultiValueDict
from rest_framework import serializers

from rest_flex_fields2.serializers import FlexFieldsModelSerializer
from tests.testapp.models import Company, Person, Pet
from tests.testapp.serializers import PetSerializer


class MockRequest:
    """Minimal request stub exposing ``query_params`` and ``method``."""

    def __init__(self, query_params=None, method="GET"):
        """Initialize with an optional query params dict and HTTP method string."""
        if query_params is None:
            query_params = {}
        self.query_params = query_params
        self.method = method


class TestSerialize(TestCase):
    """End-to-end serialization tests covering omit, fields, and expand features."""

    def test_basic_field_omit(self):
        """Fields listed in ``omit`` are absent from serialized output."""
        pet = Pet(
            name="Garfield",
            toys="paper ball, string",
            species="cat",
            owner=Person(name="Fred"),
        )

        expected_serializer_data = {
            "name": "Garfield",
            "toys": "paper ball, string",
            "diet": "",
            "sold_from": None,
        }

        serializer = PetSerializer(pet, omit=["species", "owner"])
        self.assertEqual(serializer.data, expected_serializer_data)

        serializer = PetSerializer(pet, omit=(field for field in ("species", "owner")))
        self.assertEqual(serializer.data, expected_serializer_data)

    def test_nested_field_omit(self):
        """Dot-notation ``omit`` values remove fields at the correct nesting level."""
        pet = Pet(
            name="Garfield",
            toys="paper ball, string",
            species="cat",
            owner=Person(name="Fred", employer=Company(name="McDonalds")),
        )

        expected_serializer_data = {
            "diet": "",
            "name": "Garfield",
            "toys": "paper ball, string",
            "species": "cat",
            "owner": {"hobbies": "", "employer": {"name": "McDonalds"}},
            "sold_from": None,
        }

        serializer = PetSerializer(
            pet, expand=["owner.employer"], omit=["owner.name", "owner.employer.public"]
        )

        self.assertEqual(serializer.data, expected_serializer_data)

        serializer = PetSerializer(
            pet,
            expand=(field for field in ("owner.employer",)),
            omit=(field for field in ("owner.name", "owner.employer.public")),
        )
        self.assertEqual(serializer.data, expected_serializer_data)

    def test_basic_field_include(self):
        """Sparse ``fields`` list restricts output to the specified fields only."""
        pet = Pet(
            name="Garfield",
            toys="paper ball, string",
            species="cat",
            owner=Person(name="Fred"),
        )

        expected_serializer_data = {"name": "Garfield", "toys": "paper ball, string"}

        serializer = PetSerializer(pet, fields=["name", "toys"])
        self.assertEqual(serializer.data, expected_serializer_data)

        serializer = PetSerializer(pet, fields=(field for field in ("name", "toys")))
        self.assertEqual(serializer.data, expected_serializer_data)

    def test_nested_field_include(self):
        """Dot-notation ``fields`` list restricts nested fields at the correct level."""
        pet = Pet(
            name="Garfield",
            toys="paper ball, string",
            species="cat",
            owner=Person(name="Fred", employer=Company(name="McDonalds")),
        )

        expected_serializer_data = {"owner": {"employer": {"name": "McDonalds"}}}

        serializer = PetSerializer(
            pet, expand=["owner.employer"], fields=["owner.employer.name"]
        )
        self.assertEqual(serializer.data, expected_serializer_data)

        serializer = PetSerializer(
            pet,
            expand=(field for field in ("owner.employer",)),
            fields=(field for field in ("owner.employer.name",)),
        )
        self.assertEqual(serializer.data, expected_serializer_data)

    def test_basic_expand(self):
        """``expand`` replaces a PK field with the full nested serializer output."""
        pet = Pet(
            name="Garfield",
            toys="paper ball, string",
            species="cat",
            owner=Person(name="Fred", hobbies="sailing"),
        )

        expected_serializer_data = {
            "name": "Garfield",
            "toys": "paper ball, string",
            "species": "cat",
            "owner": {"name": "Fred", "hobbies": "sailing"},
            "sold_from": None,
            "diet": "",
        }

        request = MockRequest(query_params=MultiValueDict({"expand": ["owner"]}))
        serializer = PetSerializer(pet, context={"request": request})
        self.assertEqual(serializer.data, expected_serializer_data)

        serializer_with_context = cast(serializers.Serializer, serializer)
        self.assertEqual(
            cast(serializers.Serializer, serializer_with_context.fields["owner"])
            .context.get("request"),
            request,
        )

        serializer = PetSerializer(pet, expand=(field for field in ("owner",)))
        self.assertEqual(serializer.data, expected_serializer_data)

    def test_nested_expand(self):
        """Dot-notation ``expand`` expands fields at multiple nesting levels."""
        pet = Pet(
            name="Garfield",
            toys="paper ball, string",
            species="cat",
            owner=Person(
                name="Fred", hobbies="sailing", employer=Company(name="McDonalds")
            ),
        )

        expected_serializer_data = {
            "diet": "",
            "name": "Garfield",
            "toys": "paper ball, string",
            "species": "cat",
            "owner": {
                "name": "Fred",
                "hobbies": "sailing",
                "employer": {"public": False, "name": "McDonalds"},
            },
            "sold_from": None,
        }

        request = MockRequest(
            query_params=MultiValueDict({"expand": ["owner.employer"]})
        )
        serializer = PetSerializer(pet, context={"request": request})
        self.assertEqual(serializer.data, expected_serializer_data)

        serializer_with_context = cast(serializers.Serializer, serializer)
        owner_serializer = cast(
            serializers.Serializer,
            serializer_with_context.fields["owner"],
        )
        self.assertEqual(
            cast(serializers.Serializer, owner_serializer.fields["employer"])
            .context.get("request"),
            request,
        )

        serializer = PetSerializer(pet, expand=(field for field in ("owner.employer",)))
        self.assertEqual(serializer.data, expected_serializer_data)

    def test_expand_from_request(self):
        """``expand`` values from the request query param are applied correctly."""
        pet = Pet(
            name="Garfield",
            toys="paper ball, string",
            species="cat",
            owner=Person(
                name="Fred", hobbies="sailing", employer=Company(name="McDonalds")
            ),
        )

        request = MockRequest(
            query_params=MultiValueDict({"expand": ["owner.employer"]})
        )
        serializer = PetSerializer(pet, context={"request": request})

        self.assertEqual(
            serializer.data,
            {
                "diet": "",
                "name": "Garfield",
                "toys": "paper ball, string",
                "species": "cat",
                "sold_from": None,
                "owner": {
                    "name": "Fred",
                    "hobbies": "sailing",
                    "employer": {"public": False, "name": "McDonalds"},
                },
            },
        )

    @patch("rest_flex_fields2.serializers.EXPAND_PARAM", "include")
    def test_expand_with_custom_param_name(self):
        """A custom ``EXPAND_PARAM`` name is used as the kwarg / query-param key."""
        pet = Pet(
            name="Garfield",
            toys="paper ball, string",
            species="cat",
            owner=Person(name="Fred", hobbies="sailing"),
        )

        expected_serializer_data = {
            "diet": "",
            "name": "Garfield",
            "toys": "paper ball, string",
            "species": "cat",
            "owner": {"name": "Fred", "hobbies": "sailing"},
            "sold_from": None,
        }

        serializer = PetSerializer(pet, include=["owner"])
        self.assertEqual(serializer.data, expected_serializer_data)

    @patch("rest_flex_fields2.serializers.OMIT_PARAM", "exclude")
    def test_omit_with_custom_param_name(self):
        """A custom ``OMIT_PARAM`` name is used as the kwarg / query-param key."""
        pet = Pet(
            name="Garfield",
            toys="paper ball, string",
            species="cat",
            owner=Person(name="Fred"),
        )

        expected_serializer_data = {
            "name": "Garfield",
            "toys": "paper ball, string",
            "diet": "",
            "sold_from": None,
        }

        serializer = PetSerializer(pet, exclude=["species", "owner"])
        self.assertEqual(serializer.data, expected_serializer_data)

    @patch("rest_flex_fields2.serializers.FIELDS_PARAM", "only")
    def test_fields_include_with_custom_param_name(self):
        """A custom ``FIELDS_PARAM`` name is used as the kwarg / query-param key."""
        pet = Pet(
            name="Garfield",
            toys="paper ball, string",
            species="cat",
            owner=Person(name="Fred"),
        )

        expected_serializer_data = {"name": "Garfield", "toys": "paper ball, string"}

        serializer = PetSerializer(pet, only=["name", "toys"])
        self.assertEqual(serializer.data, expected_serializer_data)

    def test_all_special_value_in_serialize(self):
        """Sparse ``fields`` containing ``__all__`` works correctly with validation."""
        class PetSerializer(FlexFieldsModelSerializer):
            owner = serializers.PrimaryKeyRelatedField(
                queryset=Person.objects.all(), allow_null=True
            )

            class Meta:
                model = Pet
                fields = "__all__"

        serializer = PetSerializer(
            fields=("name", "toys"),
            data={
                "name": "Garfield",
                "toys": "paper ball",
                "species": "cat",
                "owner": None,
                "diet": "lasagna",
            },
        )

        serializer.is_valid(raise_exception=True)
