"""Unit tests for low-level ``FlexFieldsModelSerializer`` helper methods."""

from typing import cast
from unittest import TestCase
from unittest.mock import patch, PropertyMock
from types import SimpleNamespace

from django.test import override_settings
from django.utils.datastructures import MultiValueDict
from rest_framework import serializers

from rest_flex_fields2 import FlexFieldsModelSerializer
from tests.testapp.models import Pet
from tests.testapp.serializers import PersonSerializer, PetSerializer


class MockRequest:
    """Minimal request stub exposing ``query_params`` and ``method``."""

    def __init__(self, query_params=None, method="GET"):
        """Initialize with optional query params dict and HTTP method string."""
        if query_params is None:
            query_params = MultiValueDict()
        self.query_params = query_params
        self.method = method


class TestFlexFieldModelSerializer(TestCase):
    """Tests for internal helper methods of ``FlexFieldsSerializerMixin``."""

    def test_field_should_not_exist_if_omitted(self):
        """Field listed in ``omit_fields`` must not exist."""
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer())
        result = serializer._should_field_exist("name", ["name"], [], [])
        self.assertFalse(result)

    def test_field_should_not_exist_if_not_in_sparse(self):
        """Field absent from sparse ``fields`` list must not exist."""
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer())
        result = serializer._should_field_exist("name", [], ["age"], [])
        self.assertFalse(result)

    def test_field_should_exist_if_ommitted_but_is_parent_of_omit(self):
        """Field in ``omit_fields`` that is a parent of a deeper omit must still exist."""
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer())

        result = serializer._should_field_exist(
            "employer", ["employer"], [], ["employer"]
        )

        self.assertTrue(result)

    def test_clean_fields(self):
        """``_get_fields_names_to_remove`` returns omitted field names."""
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer())
        fields = {"cat": 1, "dog": 2, "zebra": 3}
        result = serializer._get_fields_names_to_remove(list(fields.keys()), ["cat"], [], [])
        self.assertEqual(result, ["cat"])

    def test_get_expanded_field_names_if_all(self):
        """Wildcard ``*`` expands all declared expandable fields."""
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer())
        serializer.expandable_fields = {"cat": "field", "dog": "field"}
        result = serializer._get_expanded_field_names(["*"], [], [], [])
        self.assertEqual(result, ["cat", "dog"])

    def test_get_expanded_names_but_not_omitted(self):
        """Omitted fields are excluded from the expanded-field list."""
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer())
        serializer.expandable_fields = {"cat": "field", "dog": "field"}
        result = serializer._get_expanded_field_names(["cat", "dog"], ["cat"], [], [])
        self.assertEqual(result, ["dog"])

    def test_get_expanded_names_but_only_sparse(self):
        """Sparse-fieldset restrictions are respected when collecting expand names."""
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer())
        serializer.expandable_fields = {"cat": "field", "dog": "field"}
        result = serializer._get_expanded_field_names(["cat"], [], ["cat"], [])
        self.assertEqual(result, ["cat"])

    def test_get_expanded_names_including_omitted_when_defer_to_next_level(self):
        """Omit rule targeting a deeper level does not block expansion at current level."""
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer())
        serializer.expandable_fields = {"cat": "field", "dog": "field"}
        result = serializer._get_expanded_field_names(
            ["cat"], ["cat"], [], ["cat"]
        )
        self.assertEqual(result, ["cat"])

    def test_get_query_param_value_should_return_empty_if_not_root_serializer(self):
        """Nested serializers return an empty list from ``_get_query_param_value``."""
        serializer = cast(
            FlexFieldsModelSerializer,
            FlexFieldsModelSerializer(
            context={
                "request": MockRequest(
                    method="GET", query_params=MultiValueDict({"expand": ["cat"]})
                )
            },
            ),
        )
        serializer.parent = "Another serializer here"
        self.assertEqual(serializer._get_query_param_value("expand"), [])

    def test_get_omit_input_from_explicit_settings(self):
        """Explicit ``omit`` kwarg overrides the ``omit`` query param."""
        serializer = cast(
            FlexFieldsModelSerializer,
            FlexFieldsModelSerializer(
            omit=["fish"],
            context={
                "request": MockRequest(
                    method="GET", query_params=MultiValueDict({"omit": "cat,dog"})
                )
            },
            ),
        )

        self.assertEqual(serializer._flex_options_all["omit"], ["fish"])

    def test_set_omit_input_from_query_param(self):
        """``omit`` values are parsed from a comma-separated query param."""
        serializer = cast(
            FlexFieldsModelSerializer,
            FlexFieldsModelSerializer(
            context={
                "request": MockRequest(
                    method="GET", query_params=MultiValueDict({"omit": ["cat,dog"]})
                )
            }
            ),
        )
        self.assertEqual(serializer._flex_options_all["omit"], ["cat", "dog"])

    def test_set_fields_input_from_explicit_settings(self):
        """Explicit ``fields`` kwarg overrides the ``fields`` query param."""
        serializer = cast(
            FlexFieldsModelSerializer,
            FlexFieldsModelSerializer(
            fields=["fish"],
            context={
                "request": MockRequest(
                    method="GET", query_params=MultiValueDict({"fields": "cat,dog"})
                )
            },
            ),
        )

        self.assertEqual(serializer._flex_options_all["fields"], ["fish"])

    def test_set_fields_input_from_query_param(self):
        """``fields`` values are parsed from a comma-separated query param."""
        serializer = cast(
            FlexFieldsModelSerializer,
            FlexFieldsModelSerializer(
            context={
                "request": MockRequest(
                    method="GET", query_params=MultiValueDict({"fields": ["cat,dog"]})
                )
            }
            ),
        )

        self.assertEqual(serializer._flex_options_all["fields"], ["cat", "dog"])

    def test_set_fields_input_from_explicit_setting(self):
        """Explicit ``fields`` kwarg takes precedence over the query param value."""
        serializer = cast(
            FlexFieldsModelSerializer,
            FlexFieldsModelSerializer(
            fields=["cat"],
            context={
                "request": MockRequest(
                    method="GET", query_params=MultiValueDict({"fields": "cat,dog"})
                )
            },
            ),
        )

        self.assertEqual(serializer._flex_options_all["fields"], ["cat"])

    def test_set_expand_input_from_query_param(self):
        """``expand`` values are parsed from a comma-separated query param."""
        serializer = cast(
            FlexFieldsModelSerializer,
            FlexFieldsModelSerializer(
            context={
                "request": MockRequest(
                    method="GET", query_params=MultiValueDict({"expand": ["cat,dog"]})
                )
            }
            ),
        )

        self.assertEqual(serializer._flex_options_all["expand"], ["cat", "dog"])

    def test_get_expand_input_from_query_param_limit_to_list_permitted(self):
        """``expand`` values are filtered against ``context['permitted_expands']``."""
        serializer = cast(
            FlexFieldsModelSerializer,
            FlexFieldsModelSerializer(
            context={
                "request": MockRequest(
                    method="GET", query_params=MultiValueDict({"expand": ["cat,dog"]})
                ),
                "permitted_expands": ["cat"],
            }
            ),
        )

        self.assertEqual(serializer._flex_options_all["expand"], ["cat"])

    def test_parse_request_list_value(self):
        """Query param values are parsed consistently regardless of list format."""
        test_params = [
            {"abc": ["cat,dog,mouse"]},
            {"abc": ["cat", "dog", "mouse"]},
            {"abc[]": ["cat", "dog", "mouse"]},
        ]
        for query_params in test_params:
            serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer(context={}))
            serializer.context["request"] = MockRequest(
                method="GET", query_params=MultiValueDict(query_params)
            )

            result = serializer._get_query_param_value("abc")
            self.assertEqual(result, ["cat", "dog", "mouse"])

    def test_parse_request_list_value_empty_if_cannot_access_request(self):
        """Empty list is returned when the request is absent from context."""
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer(context={}))
        result = serializer._get_query_param_value("abc")
        self.assertEqual(result, [])

    def test_import_serializer_class(self):
        """``_import_serializer_class`` returns serializer classes and clear error messages."""
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer())

        resolved, error = serializer._import_serializer_class(
            "tests.testapp.serializers", "CompanySerializer"
        )

        self.assertIsNotNone(resolved)
        self.assertIsNone(error)

    def test_import_serializer_class_returns_error_when_attribute_is_not_class(self):
        """Non-class attributes are rejected with an explanatory error."""
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer())

        with patch(
            "rest_flex_fields2.serializers.importlib.import_module",
            return_value=SimpleNamespace(NotAClass=123),
        ):
            resolved, error = serializer._import_serializer_class(
                "some.path", "NotAClass"
            )

        self.assertIsNone(resolved)
        self.assertEqual(
            error,
            "Attribute NotAClass in module some.path is not a class",
        )

    def test_import_serializer_class_returns_error_when_class_is_not_serializer(self):
        """Classes that are not DRF serializers are rejected."""
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer())

        resolved, error = serializer._import_serializer_class(
            "tests.testapp.models", "Company"
        )

        self.assertIsNone(resolved)
        self.assertEqual(
            error,
            "Class Company in module tests.testapp.models is not a Serializer subclass",
        )

    def test_get_serializer_class_from_lazy_string_uses_serializers_fallback(self):
        """Lazy path resolution falls back to ``.serializers`` when needed."""
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer())

        resolved = serializer._get_serializer_class_from_lazy_string(
            "tests.testapp.PersonSerializer"
        )

        self.assertIs(resolved, PersonSerializer)

    def test_get_serializer_class_from_lazy_string_raises_for_invalid_path(self):
        """Invalid lazy serializer paths raise an exception with context."""
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer())

        with self.assertRaises(Exception) as caught:
            serializer._get_serializer_class_from_lazy_string(
                "does.not.exist.MissingSerializer"
            )

        self.assertIn("No module found at path", str(caught.exception))

    def test_make_expanded_field_serializer(self):
        """Expanded serializers receive parent/context and nested flex options."""
        serializer = cast(
            PetSerializer,
            PetSerializer(
                Pet(name="Garfield", toys="yarn", species="cat"),
                context={
                    "request": MockRequest(
                        method="GET", query_params=MultiValueDict({"expand": ["owner"]})
                    )
                },
            ),
        )

        expanded_owner = cast(
            PersonSerializer,
            serializer._make_expanded_field_serializer(
                "owner",
                {"owner": ["employer"]},
                {"owner": ["name"]},
                {"owner": ["hobbies"]},
            ),
        )

        self.assertIsInstance(expanded_owner, PersonSerializer)
        self.assertIs(expanded_owner.parent, serializer)
        self.assertIs(expanded_owner.context.get("request"), serializer.context["request"])
        self.assertEqual(expanded_owner._flex_options_base["expand"], ["employer"])
        self.assertEqual(expanded_owner._flex_options_base["fields"], ["name"])
        self.assertEqual(expanded_owner._flex_options_base["omit"], ["hobbies"])

    @patch("rest_flex_fields2.serializers.RECURSIVE_EXPANSION_PERMITTED", False)
    def test_recursive_expansion(self):
        """Recursive expansion raises ``ValidationError`` when the setting forbids it."""
        with self.assertRaises(serializers.ValidationError):
            FlexFieldsModelSerializer(
                context={
                    "request": MockRequest(
                        method="GET",
                        query_params=MultiValueDict({"expand": ["dog.leg.dog"]}),
                    )
                }
            )

    @patch(
        "rest_flex_fields2.FlexFieldsModelSerializer.recursive_expansion_permitted",
        new_callable=PropertyMock,
    )
    def test_recursive_expansion_serializer_level(
        self, mock_recursive_expansion_permitted
    ):
        """Recursive expansion raises ``ValidationError`` when the serializer attribute forbids it."""
        mock_recursive_expansion_permitted.return_value = False

        with self.assertRaises(serializers.ValidationError):
            FlexFieldsModelSerializer(
                context={
                    "request": MockRequest(
                        method="GET",
                        query_params=MultiValueDict({"expand": ["dog.leg.dog"]}),
                    )
                }
            )

    @override_settings(REST_FLEX_FIELDS={"MAXIMUM_EXPANSION_DEPTH": 3})
    def test_expansion_depth(self):
        """Expansion path within the depth limit is accepted without error."""
        serializer = cast(
            FlexFieldsModelSerializer,
            FlexFieldsModelSerializer(
            context={
                "request": MockRequest(
                    method="GET",
                    query_params=MultiValueDict({"expand": ["dog.leg.paws"]}),
                )
            }
            ),
        )
        self.assertEqual(serializer._flex_options_all["expand"], ["dog.leg.paws"])

    @patch("rest_flex_fields2.serializers.MAXIMUM_EXPANSION_DEPTH", 2)
    def test_expansion_depth_exception(self):
        """Expansion path beyond the depth limit raises ``ValidationError``."""
        with self.assertRaises(serializers.ValidationError):
            FlexFieldsModelSerializer(
                context={
                    "request": MockRequest(
                        method="GET",
                        query_params=MultiValueDict({"expand": ["dog.leg.paws"]}),
                    )
                }
            )

    @patch(
        "rest_flex_fields2.FlexFieldsModelSerializer.maximum_expansion_depth",
        new_callable=PropertyMock,
    )
    def test_expansion_depth_serializer_level(self, mock_maximum_expansion_depth):
        """Serializer-level depth attribute accepts paths within the limit."""
        mock_maximum_expansion_depth.return_value = 3
        serializer = cast(
            FlexFieldsModelSerializer,
            FlexFieldsModelSerializer(
            context={
                "request": MockRequest(
                    method="GET",
                    query_params=MultiValueDict({"expand": ["dog.leg.paws"]}),
                )
            }
            ),
        )
        self.assertEqual(serializer._flex_options_all["expand"], ["dog.leg.paws"])

    @patch(
        "rest_flex_fields2.FlexFieldsModelSerializer.maximum_expansion_depth",
        new_callable=PropertyMock,
    )
    def test_expansion_depth_serializer_level_exception(
        self, mock_maximum_expansion_depth
    ):
        """Serializer-level depth attribute raises ``ValidationError`` when limit is exceeded."""
        mock_maximum_expansion_depth.return_value = 2
        with self.assertRaises(serializers.ValidationError):
            FlexFieldsModelSerializer(
                context={
                    "request": MockRequest(
                        method="GET",
                        query_params=MultiValueDict({"expand": ["dog.leg.paws"]}),
                    )
                }
            )
