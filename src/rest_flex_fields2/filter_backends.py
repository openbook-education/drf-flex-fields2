from functools import lru_cache
import importlib
from typing import Any, Optional

from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models import QuerySet
from rest_framework import serializers
from rest_framework.filters import BaseFilterBackend
from rest_framework.viewsets import GenericViewSet
from rest_framework.request import Request

from .config import (
    EXPAND_PARAM,
    FIELDS_PARAM,
    OMIT_PARAM,
    WILDCARD_VALUES,
)
from .serializers import (
    FlexFieldsModelSerializer,
    FlexFieldsSerializerMixin,
)

WILDCARD_VALUES_JOINED = ",".join(WILDCARD_VALUES or [])


class FlexFieldsDocsFilterBackend(BaseFilterBackend):
    """
    A dummy filter backend only for schema/documentation purposes.
    """

    def filter_queryset(self, request, queryset, view):
        return queryset

    @staticmethod
    @lru_cache()
    def _get_field(field_name: str, model: models.Model) -> Optional[models.Field]:
        try:
            # noinspection PyProtectedMember
            return model._meta.get_field(field_name)
        except FieldDoesNotExist:
            return None

    @staticmethod
    def _get_expandable_fields(serializer_class: Any) -> list:
        expandable_fields = list(getattr(serializer_class.Meta, "expandable_fields").items())
        expand_list = []

        while expandable_fields:
            key, field_options = expandable_fields.pop()

            if isinstance(field_options, tuple):
                nested_serializer_class = field_options[0]
            else:
                nested_serializer_class = field_options

            if isinstance(nested_serializer_class, str):
                nested_serializer_class = FlexFieldsDocsFilterBackend._get_serializer_class_from_lazy_string(
                    nested_serializer_class
                )

            expand_list.append(key)

            meta = getattr(nested_serializer_class, "Meta", None)
            if (
                meta
                and isinstance(nested_serializer_class, type)
                and issubclass(nested_serializer_class, FlexFieldsSerializerMixin)
                and hasattr(meta, "expandable_fields")
            ):
                next_layer = getattr(meta, "expandable_fields")
                expandable_fields.extend(
                    [(f"{key}.{next_key}", next_value) for next_key, next_value in list(next_layer.items())]
                )

        return expand_list

    @staticmethod
    def _get_serializer_class_from_lazy_string(full_lazy_path: str):
        path_parts = full_lazy_path.split(".")
        class_name = path_parts.pop()
        path = ".".join(path_parts)

        serializer_class = FlexFieldsDocsFilterBackend._import_serializer_class(path, class_name)
        if serializer_class is None and not path.endswith(".serializers"):
            serializer_class = FlexFieldsDocsFilterBackend._import_serializer_class(
                f"{path}.serializers", class_name
            )

        if serializer_class:
            return serializer_class

        raise Exception(f"Could not resolve serializer class '{class_name}' from path '{path}'.")

    @staticmethod
    def _import_serializer_class(path: str, class_name: str):
        try:
            module = importlib.import_module(path)
        except ImportError:
            return None

        serializer_class = getattr(module, class_name, None)
        if isinstance(serializer_class, type) and issubclass(serializer_class, serializers.Serializer):
            return serializer_class

        return None

    @staticmethod
    def _get_fields(serializer_class):
        fields = getattr(serializer_class.Meta, "fields", [])
        return ",".join(fields)

    def get_schema_operation_parameters(self, view):
        serializer_class = view.get_serializer_class()
        if not issubclass(serializer_class, FlexFieldsSerializerMixin):
            return []

        fields = self._get_fields(serializer_class)
        expandable_fields = self._get_expandable_fields(serializer_class)
        expandable_fields.extend(WILDCARD_VALUES or [])

        parameters = [
            {
                "name": FIELDS_PARAM,
                "required": False,
                "in": "query",
                "description": "Specify required fields by comma",
                "schema": {
                    "title": "Selected fields",
                    "type": "string",
                },
                "example": (fields or "field1,field2,nested.field") + "," + WILDCARD_VALUES_JOINED,
            },
            {
                "name": OMIT_PARAM,
                "required": False,
                "in": "query",
                "description": "Specify omitted fields by comma",
                "schema": {
                    "title": "Omitted fields",
                    "type": "string",
                },
                "example": (fields or "field1,field2,nested.field") + "," + WILDCARD_VALUES_JOINED,
            },
            {
                "name": EXPAND_PARAM,
                "required": False,
                "in": "query",
                "description": "Select fields to expand",
                "style": "form",
                "explode": False,
                "schema": {
                    "title": "Expanded fields",
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": expandable_fields
                    }
                },
            },
        ]

        return parameters


class FlexFieldsFilterBackend(FlexFieldsDocsFilterBackend):
    def filter_queryset(
        self, request: Request, queryset: QuerySet, view: GenericViewSet
    ):
        if (
            not issubclass(view.get_serializer_class(), FlexFieldsSerializerMixin)
            or request.method != "GET"
        ):
            return queryset

        auto_remove_fields_from_query = getattr(
            view, "auto_remove_fields_from_query", True
        )
        auto_select_related_on_query = getattr(
            view, "auto_select_related_on_query", True
        )
        required_query_fields = list(getattr(view, "required_query_fields", []))

        serializer = view.get_serializer(  # type: FlexFieldsSerializerMixin
            context=view.get_serializer_context()
        )

        serializer.apply_flex_fields(
            serializer.fields, serializer._flex_options_rep_only
        )
        serializer._flex_fields_rep_applied = True

        model_fields = []
        nested_model_fields = []
        for field in serializer.fields.values():
            model_field = self._get_field(field.source, queryset.model)
            if model_field:
                model_fields.append(model_field)
                if field.field_name in serializer.expanded_fields or \
                        (model_field.is_relation and not model_field.many_to_one) or \
                        (model_field.is_relation and model_field.many_to_one and not model_field.concrete):  # Include GenericForeignKey
                    nested_model_fields.append(model_field)

        if auto_remove_fields_from_query:
            queryset = queryset.only(
                *(
                    required_query_fields
                    + [
                        model_field.name
                        for model_field in model_fields if (
                            not model_field.is_relation or
                            model_field.many_to_one and model_field.concrete)
                    ]
                )
            )

        if auto_select_related_on_query and nested_model_fields:
            queryset = queryset.select_related(
                *(
                    model_field.name
                    for model_field in nested_model_fields if (
                            model_field.is_relation and
                            model_field.many_to_one and
                            model_field.concrete)  # Exclude GenericForeignKey
                )
            )

            queryset = queryset.prefetch_related(*(
                model_field.name for model_field in nested_model_fields if
                (model_field.is_relation and not model_field.many_to_one) or
                (model_field.is_relation and model_field.many_to_one and not model_field.concrete)  # Include GenericForeignKey)
                )
            )

        return queryset

    @staticmethod
    @lru_cache()
    def _get_field(field_name: str, model: models.Model) -> Optional[models.Field]:
        try:
            # noinspection PyProtectedMember
            return model._meta.get_field(field_name)
        except FieldDoesNotExist:
            return None
