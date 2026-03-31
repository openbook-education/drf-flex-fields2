from typing import cast
from unittest import TestCase
from unittest.mock import patch, PropertyMock

from django.test import override_settings
from django.utils.datastructures import MultiValueDict
from rest_framework import serializers

from rest_flex_fields2 import FlexFieldsModelSerializer


class MockRequest:
    def __init__(self, query_params=None, method="GET"):
        if query_params is None:
            query_params = MultiValueDict()
        self.query_params = query_params
        self.method = method


class TestFlexFieldModelSerializer(TestCase):
    def test_field_should_not_exist_if_omitted(self):
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer())
        result = serializer._should_field_exist("name", ["name"], [], [])
        self.assertFalse(result)

    def test_field_should_not_exist_if_not_in_sparse(self):
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer())
        result = serializer._should_field_exist("name", [], ["age"], [])
        self.assertFalse(result)

    def test_field_should_exist_if_ommitted_but_is_parent_of_omit(self):
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer())

        result = serializer._should_field_exist(
            "employer", ["employer"], [], ["employer"]
        )

        self.assertTrue(result)

    def test_clean_fields(self):
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer())
        fields = {"cat": 1, "dog": 2, "zebra": 3}
        result = serializer._get_fields_names_to_remove(list(fields.keys()), ["cat"], [], [])
        self.assertEqual(result, ["cat"])

    def test_get_expanded_field_names_if_all(self):
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer())
        serializer.expandable_fields = {"cat": "field", "dog": "field"}
        result = serializer._get_expanded_field_names(["*"], [], [], [])
        self.assertEqual(result, ["cat", "dog"])

    def test_get_expanded_names_but_not_omitted(self):
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer())
        serializer.expandable_fields = {"cat": "field", "dog": "field"}
        result = serializer._get_expanded_field_names(["cat", "dog"], ["cat"], [], [])
        self.assertEqual(result, ["dog"])

    def test_get_expanded_names_but_only_sparse(self):
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer())
        serializer.expandable_fields = {"cat": "field", "dog": "field"}
        result = serializer._get_expanded_field_names(["cat"], [], ["cat"], [])
        self.assertEqual(result, ["cat"])

    def test_get_expanded_names_including_omitted_when_defer_to_next_level(self):
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer())
        serializer.expandable_fields = {"cat": "field", "dog": "field"}
        result = serializer._get_expanded_field_names(
            ["cat"], ["cat"], [], ["cat"]
        )
        self.assertEqual(result, ["cat"])

    def test_get_query_param_value_should_return_empty_if_not_root_serializer(self):
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
        self.assertFalse(serializer._get_query_param_value("expand"), [])

    def test_get_omit_input_from_explicit_settings(self):
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

    def test_set_expand_input_from_explicit_setting(self):
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
        serializer = cast(FlexFieldsModelSerializer, FlexFieldsModelSerializer(context={}))
        result = serializer._get_query_param_value("abc")
        self.assertEqual(result, [])

    def test_import_serializer_class(self):
        pass

    def test_make_expanded_field_serializer(self):
        pass

    @patch("rest_flex_fields2.serializers.RECURSIVE_EXPANSION_PERMITTED", False)
    def test_recursive_expansion(self):
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
