"""Flex-fields serializer mixin and model serializer.

Provides `FlexFieldsSerializerMixin` which adds ``fields``, ``omit``, and
``expand`` support to any DRF serializer, and the ready-to-use
`FlexFieldsModelSerializer` that combines the mixin with
``serializers.ModelSerializer``.
"""

import copy
import importlib
from typing import List, Optional, Tuple, Type

from rest_framework.serializers import (Serializer, ModelSerializer, ValidationError)

from .config import (
    EXPAND_PARAM,
    FIELDS_PARAM,
    MAXIMUM_EXPANSION_DEPTH,
    OMIT_PARAM,
    RECURSIVE_EXPANSION_PERMITTED,
    WILDCARD_VALUES,
)
from .utils import split_levels


class FlexFieldsSerializerMixin(Serializer):
    """Mixin that adds sparse-fieldset and nested-expansion support to a serializer.

    Accepts the ``fields``, ``omit``, and ``expand`` keyword arguments (names
    are configurable via ``REST_FLEX_FIELDS2`` settings) both as constructor
    kwargs and as query-string parameters on the current request.  Query
    parameters are only read on the root serializer; nested serializers
    receive their options through constructor kwargs propagated by the parent.

    Declare expandable relations either on ``Meta.expandable_fields`` (preferred)
    or directly on ``expandable_fields`` for backwards compatibility.
    """

    expandable_fields = {}
    maximum_expansion_depth: Optional[int] = None
    recursive_expansion_permitted: Optional[bool] = None

    def __init__(self, *args, **kwargs):
        """Initialize flex-fields options from kwargs and request query params."""
        expand = list(kwargs.pop(EXPAND_PARAM, []))
        fields = list(kwargs.pop(FIELDS_PARAM, []))
        omit   = list(kwargs.pop(OMIT_PARAM, []))
        parent = kwargs.pop("parent", None)

        super().__init__(*args, **kwargs)

        self.parent = parent
        self.expanded_fields = []
        self._flex_fields_rep_applied = False

        self._flex_options_base = {
            "expand": expand,
            "fields": fields,
            "omit":   omit,
        }

        self._flex_options_rep_only = {
            "expand": self._get_permitted_expands_from_query_param(EXPAND_PARAM) if not expand else [],
            "fields": self._get_query_param_value(FIELDS_PARAM) if not fields else [],
            "omit":   self._get_query_param_value(OMIT_PARAM) if not omit else [],
        }

        self._flex_options_all = {
            "expand": self._flex_options_base["expand"] + self._flex_options_rep_only["expand"],
            "fields": self._flex_options_base["fields"] + self._flex_options_rep_only["fields"],
            "omit":   self._flex_options_base["omit"]   + self._flex_options_rep_only["omit"],
        }

    def get_maximum_expansion_depth(self) -> Optional[int]:
        """Return the effective maximum expansion depth.

        Uses the serializer-level ``maximum_expansion_depth`` attribute when
        set, otherwise falls back to the ``MAXIMUM_EXPANSION_DEPTH`` setting.
        """
        return self.maximum_expansion_depth or MAXIMUM_EXPANSION_DEPTH

    def get_recursive_expansion_permitted(self) -> bool:
        """Return whether recursive expansion is allowed.

        Uses the serializer-level ``recursive_expansion_permitted`` attribute
        when set, otherwise falls back to the ``RECURSIVE_EXPANSION_PERMITTED``
        setting.
        """
        if self.recursive_expansion_permitted is not None:
            return self.recursive_expansion_permitted
        else:
            return RECURSIVE_EXPANSION_PERMITTED

    def to_representation(self, instance):
        """Apply request-sourced flex-fields options once, then delegate to super."""
        if not self._flex_fields_rep_applied:
            self.apply_flex_fields(self.fields, self._flex_options_rep_only)
            self._flex_fields_rep_applied = True

        return super().to_representation(instance)

    def get_fields(self):
        """Return fields after applying constructor-sourced flex-fields options."""
        fields = super().get_fields()
        self.apply_flex_fields(fields, self._flex_options_base)
        return fields

    def apply_flex_fields(self, fields, flex_options):
        """Apply sparse-fieldset and expansion options to `fields` in place.

        Removes fields that are excluded by ``omit`` or not present in
        ``fields`` (sparse-fieldset), then replaces fields listed in
        ``expand`` with their nested serializer instances.
        Returns the modified `fields` mapping.
        """
        expand_fields, next_expand_fields = split_levels(flex_options["expand"])
        sparse_fields, next_sparse_fields = split_levels(flex_options["fields"])
        omit_fields, next_omit_fields = split_levels(flex_options["omit"])

        for field_name in self._get_fields_names_to_remove(
            list(fields.keys()), omit_fields, sparse_fields, list(next_omit_fields.keys())
        ):
            fields.pop(field_name)

        for name in self._get_expanded_field_names(
            expand_fields, omit_fields, sparse_fields, list(next_omit_fields.keys())
        ):
            self.expanded_fields.append(name)

            fields[name] = self._make_expanded_field_serializer(
                name, next_expand_fields, next_sparse_fields, next_omit_fields
            )

        return fields

    def _make_expanded_field_serializer(
        self, name, nested_expand, nested_fields, nested_omit
    ):
        """Build and return the nested serializer instance for an expanded field.

        Looks up `name` in ``_expandable_fields``, resolves any lazy string
        path to a concrete class, then instantiates the serializer with the
        appropriate ``context``, ``parent``, ``expand``, ``fields``, and
        ``omit`` kwargs for the next nesting level.
        """
        field_options = self._expandable_fields[name]

        if isinstance(field_options, tuple):
            serializer_class = field_options[0]
            settings = copy.deepcopy(field_options[1]) if len(field_options) > 1 else {}
        else:
            serializer_class = field_options
            settings = {}

        if isinstance(serializer_class, str):
            serializer_class = self._get_serializer_class_from_lazy_string(serializer_class)

        if issubclass(serializer_class, Serializer):
            settings["context"] = self.context

        if issubclass(serializer_class, FlexFieldsSerializerMixin):
            settings["parent"] = self

            if name in nested_expand:
                settings[EXPAND_PARAM] = nested_expand[name]

            if name in nested_fields:
                settings[FIELDS_PARAM] = nested_fields[name]

            if name in nested_omit:
                settings[OMIT_PARAM] = nested_omit[name]

        return serializer_class(**settings)

    def _get_serializer_class_from_lazy_string(self, full_lazy_path: str) -> Type[Serializer]:
        """Resolve a dotted string path to a serializer class.

        Tries the exact path first; if that fails and the path does not
        already end in ``.serializers``, appends ``.serializers`` and retries.
        Raises ``Exception`` when the class cannot be found.
        """
        path_parts = full_lazy_path.split(".")
        class_name = path_parts.pop()
        path = ".".join(path_parts)
        serializer_class, error = self._import_serializer_class(path, class_name)

        if error and not path.endswith(".serializers"):
            serializer_class, error = self._import_serializer_class(
                path + ".serializers", class_name
            )

        if serializer_class:
            return serializer_class

        raise Exception(error)

    def _import_serializer_class(self, path: str, class_name: str) -> Tuple[Optional[Type[Serializer]], Optional[str]]:
        """Import `class_name` from the module at `path`.

        Returns a ``(serializer_class, None)`` tuple on success, or
        ``(None, error_message)`` when the module cannot be imported, the
        attribute does not exist, or the attribute is not a
        ``Serializer`` subclass.
        """
        try:
            module = importlib.import_module(path)
        except ImportError:
            return None, f"No module found at path: {path} when trying to import {class_name}"

        try:
            resolved = getattr(module, class_name)
        except AttributeError:
            return None, f"No class {class_name} class found in module {path}"

        # Validate that the resolved attribute is actually a serializer class
        if not isinstance(resolved, type):
            return None, f"Attribute {class_name} in module {path} is not a class"

        if not issubclass(resolved, Serializer):
            return None, f"Class {class_name} in module {path} is not a Serializer subclass"

        return resolved, None

    def _get_fields_names_to_remove(
        self,
        current_fields: List[str],
        omit_fields: List[str],
        sparse_fields: List[str],
        next_level_omits: List[str],
    ) -> List[str]:
        """Return a list of field names that should be removed from the serializer.

        A field is removed when it appears in `omit_fields`, or when
        `sparse_fields` is non-empty and the field is not listed there.
        Fields in `next_level_omits` are never removed at this level because
        their omit rule targets a deeper nesting (e.g. ``omit=house.rooms.kitchen``
        must not remove ``house`` or ``rooms``).
        """
        sparse = len(sparse_fields) > 0
        to_remove = []

        if not sparse and len(omit_fields) == 0:
            return to_remove

        for field_name in current_fields:
            should_exist = self._should_field_exist(field_name, omit_fields, sparse_fields, next_level_omits)

            if not should_exist:
                to_remove.append(field_name)

        return to_remove

    def _should_field_exist(
        self,
        field_name: str,
        omit_fields: List[str],
        sparse_fields: List[str],
        next_level_omits: List[str],
    ) -> bool:
        """Return whether `field_name` should be kept in the serializer output.

        `next_level_omits` contains field names whose omit rule targets a
        deeper nesting level; they must not be removed at the current level
        (e.g. ``omit=house.rooms.kitchen`` must preserve ``house`` and
        ``rooms``).
        """
        if field_name in omit_fields and field_name not in next_level_omits:
            return False
        elif self._contains_wildcard_value(sparse_fields):
            return True
        elif len(sparse_fields) > 0 and field_name not in sparse_fields:
            return False
        else:
            return True

    def _get_expanded_field_names(
        self,
        expand_fields: List[str],
        omit_fields: List[str],
        sparse_fields: List[str],
        next_level_omits: List[str],
    ) -> List[str]:
        """Return the validated list of field names to expand.

        Wildcards are resolved to all declared expandable field names.
        Fields not present in ``_expandable_fields``, or excluded by the
        sparse-fieldset / omit rules, are silently skipped.
        """
        if len(expand_fields) == 0:
            return []

        if self._contains_wildcard_value(expand_fields):
            expand_fields = list(self._expandable_fields.keys())

        expanded_field_names = []

        for name in expand_fields:
            if name not in self._expandable_fields:
                continue

            if not self._should_field_exist(
                name, omit_fields, sparse_fields, next_level_omits
            ):
                continue

            expanded_field_names.append(name)

        return expanded_field_names

    @property
    def _expandable_fields(self) -> dict:
        """Return the mapping of expandable field names to their serializer config.

        Prefers ``Meta.expandable_fields`` for consistency with the DRF
        convention of placing serializer metadata on the inner ``Meta`` class.
        Falls back to the class-level ``expandable_fields`` attribute for
        backwards compatibility.
        """
        meta = getattr(self, "Meta", None)

        if meta is not None and hasattr(meta, "expandable_fields"):
            return meta.expandable_fields

        return self.expandable_fields

    def _get_query_param_value(self, field: str) -> List[str]:
        """Return the parsed query-parameter values for `field`.

        Only reads query parameters on the root serializer (i.e. when
        ``self.parent`` is ``None``).  Supports both plain repeated params
        (``field=a,b``) and bracket-style params (``field[]=a``).  Runs
        recursive-expansion and depth validation on every returned path.
        Returns an empty list when the parameter is absent or this is a
        nested serializer.
        """
        if self.parent:
            return []

        if not hasattr(self, "context") or not self.context.get("request"):
            return []

        values = self.context["request"].query_params.getlist(field)

        if not values:
            values = self.context["request"].query_params.getlist(f"{field}[]")

        if values and len(values) == 1:
            values = values[0].split(",")

        for expand_path in values:
            self._validate_recursive_expansion(expand_path)
            self._validate_expansion_depth(expand_path)

        return values or []

    def _split_expand_field(self, expand_path: str) -> List[str]:
        """Split a dot-separated expand path into its individual segments."""
        return expand_path.split(".")  # noqa: E501

    def recursive_expansion_not_permitted(self):
        """Raise a validation error indicating recursive expansion.

        Override this method to raise a custom exception instead of the
        default ``ValidationError``.
        """
        raise ValidationError(detail="Recursive expansion found")

    def _validate_recursive_expansion(self, expand_path: str) -> None:
        """Raise when `expand_path` contains a repeated segment.

        Parses the dot-separated `expand_path` and checks for duplicate
        segments.  Does nothing when recursive expansion is permitted
        (``RECURSIVE_EXPANSION_PERMITTED`` is ``True``).
        """
        recursive_expansion_permitted = self.get_recursive_expansion_permitted()
        if recursive_expansion_permitted is True:
            return

        expansion_path = self._split_expand_field(expand_path)
        expansion_length = len(expansion_path)
        expansion_length_unique = len(set(expansion_path))

        if expansion_length != expansion_length_unique:
            self.recursive_expansion_not_permitted()

    def expansion_depth_exceeded(self):
        """Raise a validation error indicating the expansion depth limit was exceeded.

        Override this method to raise a custom exception instead of the
        default ``ValidationError``.
        """
        raise ValidationError(detail="Expansion depth exceeded")

    def _validate_expansion_depth(self, expand_path: str) -> None:
        """Raise when `expand_path` exceeds the configured maximum depth.

        Counts the dot-separated segments of `expand_path` and compares
        against ``get_maximum_expansion_depth()``.  Does nothing when no
        maximum depth is configured.
        """
        maximum_expansion_depth = self.get_maximum_expansion_depth()
        if maximum_expansion_depth is None:
            return

        expansion_path = self._split_expand_field(expand_path)
        if len(expansion_path) > maximum_expansion_depth:
            self.expansion_depth_exceeded()

    def _get_permitted_expands_from_query_param(self, expand_param: str) -> List[str]:
        """Return the expand list filtered by ``permitted_expands`` from context.

        When ``permitted_expands`` is present in the serializer context (e.g.
        set by `FlexFieldsMixin` for list actions), wildcard expansion is
        resolved to the full permitted list, and any other values are
        intersected with it.  Returns the unfiltered expand list when no
        permission constraint is active.
        """
        expand = self._get_query_param_value(expand_param)

        if "permitted_expands" in self.context:
            permitted_expands = self.context["permitted_expands"]

            if self._contains_wildcard_value(expand):
                return permitted_expands
            else:
                return list(set(expand) & set(permitted_expands))

        return expand

    def _contains_wildcard_value(self, expand_values: List[str]) -> bool:
        """Return whether `expand_values` contains any configured wildcard token.

        Always returns ``False`` when ``WILDCARD_VALUES`` is ``None``
        (wildcards disabled).
        """
        if WILDCARD_VALUES is None:
            return False

        intersecting_values = list(set(expand_values) & set(WILDCARD_VALUES))
        return len(intersecting_values) > 0


class FlexFieldsModelSerializer(FlexFieldsSerializerMixin, ModelSerializer):
    """Convenience serializer combining `FlexFieldsSerializerMixin` with ``ModelSerializer``.

    Drop-in replacement for ``serializers.ModelSerializer`` that adds
    sparse-fieldset (``fields``, ``omit``) and nested-expansion (``expand``)
    support out of the box.
    """
