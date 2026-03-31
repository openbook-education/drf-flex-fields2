"""Integration tests for view-layer behaviour including filter-backend query optimisation."""

from http import HTTPStatus
from types import SimpleNamespace
from typing import cast
from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from django.utils.datastructures import MultiValueDict
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APITestCase
from rest_framework.viewsets import GenericViewSet

from rest_flex_fields2.filter_backends import FlexFieldsFilterBackend
from rest_flex_fields2.config import EXPAND_PARAM, FIELDS_PARAM, OMIT_PARAM, WILDCARD_VALUES
from rest_flex_fields2.filter_backends import FlexFieldsDocsFilterBackend
from tests.testapp.models import Company, Person, Pet, PetStore, TaggedItem
from tests.testapp.serializers import PetStoreSerializer
from tests.testapp.views import PetViewSet


class PetViewTests(APITestCase):
    """API tests for ``PetViewSet`` covering expand, sparse-fieldset, and write operations."""

    def setUp(self):
        """Create a ``Company``, ``Person``, and ``Pet`` for use in each test."""
        self.company = Company.objects.create(name="McDonalds")

        self.person = Person.objects.create(
            name="Fred", hobbies="sailing", employer=self.company
        )

        self.pet = Pet.objects.create(
            name="Garfield", toys="paper ball, string", species="cat", owner=self.person
        )

    def tearDown(self):
        """Delete all test objects after each test."""
        Company.objects.all().delete()
        Person.objects.all().delete()
        Pet.objects.all().delete()

    def test_retrieve_expanded(self):
        """Retrieve endpoint returns expanded owner when ``?expand=owner`` is given."""
        url = reverse("pet-detail", args=[self.pet.pk])
        response = cast(Response, self.client.get(url + "?expand=owner", format="json"))

        self.assertEqual(
            response.data,
            {
                "diet": "",
                "name": "Garfield",
                "toys": "paper ball, string",
                "species": "cat",
                "sold_from": None,
                "owner": {"name": "Fred", "hobbies": "sailing"},
            },
        )

    def test_retrieve_sparse(self):
        """Retrieve endpoint returns only requested fields when ``?fields=`` is given."""
        url = reverse("pet-detail", args=[self.pet.pk])
        response = cast(
            Response,
            self.client.get(url + "?fields=name,species", format="json"),
        )

        self.assertEqual(response.data, {"name": "Garfield", "species": "cat"})

    def test_retrieve_sparse_and_deep_expanded(self):
        """Sparse fieldset and deep expansion can be combined in one request."""
        url = reverse("pet-detail", args=[self.pet.pk])
        url = url + "?fields=owner&expand=owner.employer"
        response = cast(Response, self.client.get(url, format="json"))

        self.assertEqual(
            response.data,
            {
                "owner": {
                    "name": "Fred",
                    "hobbies": "sailing",
                    "employer": {"public": False, "name": "McDonalds"},
                }
            },
        )

    def test_retrieve_all_fields_at_root_and_sparse_fields_at_next_level(self):
        """Wildcard root fieldset combined with a nested sparse fieldset is handled correctly."""
        url = reverse("pet-detail", args=[self.pet.pk])
        url = url + "?fields=*,owner.name&expand=owner"
        response = cast(Response, self.client.get(url, format="json"))

        self.assertEqual(
            response.data,
            {
                "name": "Garfield",
                "toys": "paper ball, string",
                "species": "cat",
                "diet": "",
                "sold_from": None,
                "owner": {
                    "name": "Fred",
                },
            },
        )

    def test_list_expanded(self):
        """List endpoint returns expanded owner when ``?expand=owner`` is given."""
        url = reverse("pet-list")
        url = url + "?expand=owner"
        response = cast(Response, self.client.get(url, format="json"))
        response_data = cast(list[dict[str, object]], response.data)

        self.assertEqual(
            response_data[0],
            {
                "diet": "",
                "name": "Garfield",
                "toys": "paper ball, string",
                "species": "cat",
                "sold_from": None,
                "owner": {"name": "Fred", "hobbies": "sailing"},
            },
        )

    def test_list_disallowed_expand_is_filtered_by_permit_list_expands(self):
        """List endpoint filters disallowed expand values based on ``permit_list_expands``."""
        url = reverse("pet-list")
        response = cast(Response, self.client.get(url + "?expand=diet", format="json"))
        response_data = cast(list[dict[str, object]], response.data)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response_data[0]["diet"], "")

    def test_list_wildcard_expand_respects_permit_list_expands(self):
        """Wildcard expansion on list only expands fields included in ``permit_list_expands``."""
        url = reverse("pet-list")
        response = cast(Response, self.client.get(url + "?expand=*", format="json"))
        response_data = cast(list[dict[str, object]], response.data)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response_data[0]["owner"],
            {"name": "Fred", "hobbies": "sailing"},
        )
        self.assertEqual(response_data[0]["diet"], "")

    def test_create_and_return_expanded_field(self):
        """Create endpoint returns the expanded relation in its response payload."""
        url = reverse("pet-list")
        url = url + "?expand=owner"

        response = cast(
            Response,
            self.client.post(
            url,
            {
                "diet": "rats",
                "owner": self.person.pk,
                "species": "snake",
                "toys": "playstation",
                "name": "Freddy",
                "sold_from": None,
            },
            format="json",
            ),
        )

        self.assertEqual(
            response.data,
            {
                "name": "Freddy",
                "diet": "rats",
                "toys": "playstation",
                "sold_from": None,
                "species": "snake",
                "owner": {"name": "Fred", "hobbies": "sailing"},
            },
        )

    def test_expand_drf_serializer_field(self):
        """A plain DRF ``SerializerMethodField`` can be declared as an expandable field."""
        url = reverse("pet-detail", args=[self.pet.pk])
        response = cast(Response, self.client.get(url + "?expand=diet", format="json"))

        self.assertEqual(
            response.data,
            {
                "diet": "homemade lasanga",
                "name": "Garfield",
                "toys": "paper ball, string",
                "sold_from": None,
                "species": "cat",
                "owner": self.pet.owner.pk,
            },
        )

    def test_expand_drf_model_serializer(self):
        """A plain ``ModelSerializer`` (non-flex) can be an expandable field target."""
        petco = PetStore.objects.create(name="PetCo")
        self.pet.sold_from = petco
        self.pet.save()

        url = reverse("pet-detail", args=[self.pet.pk])
        response = cast(
            Response,
            self.client.get(url + "?expand=sold_from", format="json"),
        )

        self.assertEqual(
            response.data,
            {
                "diet": "",
                "name": "Garfield",
                "toys": "paper ball, string",
                "sold_from": {"id": petco.pk, "name": "PetCo"},
                "species": "cat",
                "owner": self.pet.owner.pk,
            },
        )


@override_settings(DEBUG=True)
@patch("tests.testapp.views.PetViewSet.filter_backends", [FlexFieldsFilterBackend])
class PetViewWithSelectFieldsFilterBackendTests(PetViewTests):
    """Re-runs all ``PetViewTests`` with ``FlexFieldsFilterBackend`` active."""

    def test_query_optimization(self):
        """Filter backend generates a single optimised SQL query for sparse + expand requests."""
        url = reverse("pet-list")
        url = url + "?expand=owner&fields=name,owner"

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertEqual(len(connection.queries), 1)
        self.assertEqual(
            connection.queries[0]["sql"],
            (
                "SELECT "
                '"testapp_pet"."id", '
                '"testapp_pet"."name", '
                '"testapp_pet"."owner_id", '
                '"testapp_person"."id", '
                '"testapp_person"."name", '
                '"testapp_person"."hobbies", '
                '"testapp_person"."employer_id" '
                'FROM "testapp_pet" '
                'INNER JOIN "testapp_person" ON ("testapp_pet"."owner_id" = "testapp_person"."id")'
            ),
        )

@override_settings(DEBUG=True)
@patch("tests.testapp.views.TaggedItemViewSet.filter_backends", [FlexFieldsFilterBackend])
class TaggedItemViewWithSelectFieldsFilterBackendTests(APITestCase):
    """Tests for ``FlexFieldsFilterBackend`` with ``GenericForeignKey`` relations."""

    def test_query_optimization_includes_generic_foreign_keys_in_prefetch_related(self):
        """``GenericForeignKey`` fields are included in ``prefetch_related`` calls."""
        self.company = Company.objects.create(name="McDonalds")

        self.person = Person.objects.create(
            name="Fred", hobbies="sailing", employer=self.company
        )

        self.pet1 = Pet.objects.create(
            name="Garfield", toys="paper ball, string", species="cat",
            owner=self.person
        )
        self.pet2 = Pet.objects.create(
            name="Garfield", toys="paper ball, string", species="cat",
            owner=self.person
        )

        self.tagged_item1 = TaggedItem.objects.create(
            content_type=ContentType.objects.get_for_model(Pet),
            object_id=self.pet1.pk
        )
        self.tagged_item2 = TaggedItem.objects.create(
            content_type=ContentType.objects.get_for_model(Pet),
            object_id=self.pet2.pk
        )
        self.tagged_item3 = TaggedItem.objects.create(
            content_type=ContentType.objects.get_for_model(Person),
            object_id=self.person.pk
        )
        self.tagged_item4 = TaggedItem.objects.create(
            content_type=ContentType.objects.get_for_model(Company),
            object_id=self.company.pk
        )

        url = reverse("tagged-item-list")

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(connection.queries), 4)

        self.assertEqual(
            connection.queries[0]["sql"],
            (
                'SELECT '
                '"testapp_taggeditem"."id", '
                '"testapp_taggeditem"."content_type_id", '
                '"testapp_taggeditem"."object_id", '
                '"django_content_type"."id", '
                '"django_content_type"."app_label", '
                '"django_content_type"."model" '
                'FROM "testapp_taggeditem" '
                'INNER JOIN "django_content_type" ON ("testapp_taggeditem"."content_type_id" = "django_content_type"."id")'
            ))
        self.assertEqual(
            connection.queries[1]["sql"],
            (
                'SELECT '
                '"testapp_pet"."id", '
                '"testapp_pet"."name", '
                '"testapp_pet"."toys", '
                '"testapp_pet"."species", '
                '"testapp_pet"."owner_id", '
                '"testapp_pet"."sold_from_id", '
                '"testapp_pet"."diet" '
                'FROM "testapp_pet" WHERE "testapp_pet"."id" IN ({0}, {1})'.format(self.pet1.pk, self.pet2.pk)
            )
        )
        self.assertEqual(
            connection.queries[2]["sql"],
            (
                'SELECT '
                '"testapp_person"."id", '
                '"testapp_person"."name", '
                '"testapp_person"."hobbies", '
                '"testapp_person"."employer_id" '
                'FROM "testapp_person" WHERE "testapp_person"."id" IN ({0})'.format(self.person.pk)
            )
        )
        self.assertEqual(
            connection.queries[3]["sql"],
            (
                'SELECT '
                '"testapp_company"."id", '
                '"testapp_company"."name", '
                '"testapp_company"."public" '
                'FROM "testapp_company" WHERE "testapp_company"."id" IN ({0})'.format(self.company.pk)
            )
        )

        self.assertEqual(len(response.json()), 4)


class FlexFieldsDocsFilterBackendSchemaTests(TestCase):
    """Tests for the OpenAPI schema parameters emitted by ``FlexFieldsDocsFilterBackend``."""

    def setUp(self):
        """Instantiate the backend under test."""
        self.backend = FlexFieldsDocsFilterBackend()

    def test_get_schema_operation_parameters_for_flex_fields_view(self):
        """Schema parameters include ``fields``, ``omit``, and ``expand`` for flex-fields views."""
        view = PetViewSet()

        parameters = self.backend.get_schema_operation_parameters(view)

        self.assertEqual(len(parameters), 3)
        self.assertEqual([p["name"] for p in parameters], [FIELDS_PARAM, OMIT_PARAM, EXPAND_PARAM])

        fields_parameter = next(p for p in parameters if p["name"] == FIELDS_PARAM)
        self.assertEqual(fields_parameter["schema"]["type"], "string")
        self.assertIn("example", fields_parameter)

        omit_parameter = next(p for p in parameters if p["name"] == OMIT_PARAM)
        self.assertEqual(omit_parameter["schema"]["type"], "string")
        self.assertIn("example", omit_parameter)

        expand_parameter = next(p for p in parameters if p["name"] == EXPAND_PARAM)
        self.assertEqual(expand_parameter["schema"]["type"], "array")
        self.assertEqual(expand_parameter["schema"]["items"]["type"], "string")

        expand_enum = expand_parameter["schema"]["items"]["enum"]
        self.assertIn("owner", expand_enum)
        self.assertIn("owner.employer", expand_enum)
        self.assertIn("sold_from", expand_enum)
        self.assertIn("diet", expand_enum)

        for wildcard_value in WILDCARD_VALUES or []:
            self.assertIn(wildcard_value, expand_enum)

    def test_get_schema_operation_parameters_for_non_flex_fields_view(self):
        """An empty list is returned for views whose serializer is not a flex-fields serializer."""
        class NonFlexFieldsViewSet:
            @staticmethod
            def get_serializer_class():
                return PetStoreSerializer

        view = NonFlexFieldsViewSet()

        parameters = self.backend.get_schema_operation_parameters(view)

        self.assertEqual(parameters, [])

    def test_filter_queryset_is_noop_for_docs_backend(self):
        """Docs backend filter method returns querysets unchanged."""
        queryset = Pet.objects.all()
        result = self.backend.filter_queryset(None, queryset, None)
        self.assertIs(result, queryset)

    def test_get_field_returns_none_for_missing_model_field(self):
        """Unknown model fields return ``None`` from helper lookup."""
        self.assertIsNone(self.backend._get_field("does_not_exist", Pet))

    def test_get_expandable_fields_returns_empty_for_non_flex_serializer(self):
        """Serializer classes without expandable metadata return an empty list."""

        class PlainSerializer:
            class Meta:
                fields = ["id"]

        self.assertEqual(self.backend._get_expandable_fields(PlainSerializer), [])

    def test_get_expandable_fields_supports_tuple_with_lazy_serializer_path(self):
        """Tuple expandable-field declarations resolve lazy serializer strings correctly."""

        class TupleExpandableSerializer:
            class Meta:
                expandable_fields = {
                    "owner": ("tests.testapp.PersonSerializer", {"read_only": True}),
                }

        expanded = self.backend._get_expandable_fields(TupleExpandableSerializer)

        self.assertIn("owner", expanded)
        self.assertIn("owner.employer", expanded)

    def test_get_serializer_class_from_lazy_string_raises_for_invalid_path(self):
        """Invalid lazy serializer paths raise an exception in schema helper logic."""
        with self.assertRaises(Exception):
            self.backend._get_serializer_class_from_lazy_string("tests.missing.Serializer")

    def test_import_serializer_class_returns_none_for_non_serializer(self):
        """Import helper returns ``None`` when target class is not a serializer."""
        result = self.backend._import_serializer_class("tests.testapp.models", "Pet")
        self.assertIsNone(result)

    def test_get_fields_returns_empty_string_when_meta_fields_missing(self):
        """Schema field helper returns an empty string when ``Meta.fields`` is absent."""

        class SerializerWithoutFields:
            class Meta:
                pass

        self.assertEqual(self.backend._get_fields(SerializerWithoutFields), "")


class FlexFieldsFilterBackendOptionTests(TestCase):
    """Unit tests for ``FlexFieldsFilterBackend`` view option branches."""

    def setUp(self):
        """Create shared data and backend instances for option tests."""
        self.company = Company.objects.create(name="McDonalds")
        self.person = Person.objects.create(
            name="Fred", hobbies="sailing", employer=self.company
        )
        self.pet = Pet.objects.create(
            name="Garfield",
            toys="paper ball, string",
            species="cat",
            owner=self.person,
        )
        self.backend = FlexFieldsFilterBackend()

    def _make_view(self, request, **attrs):
        """Create a minimal view object exposing serializer hooks required by the backend."""
        view = SimpleNamespace(**attrs)
        view.get_serializer_class = lambda: PetViewSet.serializer_class
        view.get_serializer_context = lambda: {"request": request}
        view.get_serializer = lambda *args, **kwargs: PetViewSet.serializer_class(
            *args, **kwargs
        )
        return view

    def test_filter_queryset_returns_unchanged_for_non_get(self):
        """Non-GET requests bypass query optimization and return the original queryset."""
        request = SimpleNamespace(
            method="POST",
            query_params=MultiValueDict({"fields": ["name"]}),
        )
        view = self._make_view(request)
        queryset = Pet.objects.all()

        result = self.backend.filter_queryset(
            cast(Request, request),
            queryset,
            cast(GenericViewSet, view),
        )

        self.assertIs(result, queryset)

    def test_filter_queryset_returns_unchanged_for_non_flex_serializer(self):
        """Views with non-flex serializers bypass query optimization."""
        request = SimpleNamespace(method="GET", query_params=MultiValueDict())
        view = SimpleNamespace(
            get_serializer_class=lambda: PetStoreSerializer,
            get_serializer_context=lambda: {"request": request},
            get_serializer=lambda *args, **kwargs: PetStoreSerializer(*args, **kwargs),
        )
        queryset = Pet.objects.all()

        result = self.backend.filter_queryset(
            cast(Request, request),
            queryset,
            cast(GenericViewSet, view),
        )

        self.assertIs(result, queryset)

    def test_auto_remove_fields_from_query_false_keeps_full_model_projection(self):
        """Disabling ``auto_remove_fields_from_query`` prevents ``only()`` from trimming columns."""
        request = SimpleNamespace(
            method="GET",
            query_params=MultiValueDict({"fields": ["name"]}),
        )
        view = self._make_view(request, auto_remove_fields_from_query=False)
        queryset = Pet.objects.all()

        result = self.backend.filter_queryset(
            cast(Request, request),
            queryset,
            cast(GenericViewSet, view),
        )
        sql = str(result.query)

        self.assertIn('"testapp_pet"."toys"', sql)
        self.assertIn('"testapp_pet"."species"', sql)

    def test_auto_select_related_on_query_false_avoids_join_for_expanded_relation(self):
        """Disabling ``auto_select_related_on_query`` avoids relation join optimization."""
        request = SimpleNamespace(
            method="GET",
            query_params=MultiValueDict({"expand": ["owner"], "fields": ["name,owner"]}),
        )
        view = self._make_view(request, auto_select_related_on_query=False)
        queryset = Pet.objects.all()

        result = self.backend.filter_queryset(
            cast(Request, request),
            queryset,
            cast(GenericViewSet, view),
        )
        sql = str(result.query)

        self.assertNotIn('JOIN "testapp_person"', sql)

    def test_required_query_fields_are_always_selected(self):
        """``required_query_fields`` are preserved even if sparse fields would exclude them."""
        request = SimpleNamespace(
            method="GET",
            query_params=MultiValueDict({"fields": ["name"]}),
        )
        view = self._make_view(request, required_query_fields=["species"])
        queryset = Pet.objects.all()

        result = self.backend.filter_queryset(
            cast(Request, request),
            queryset,
            cast(GenericViewSet, view),
        )
        sql = str(result.query)

        self.assertIn('"testapp_pet"."species"', sql)