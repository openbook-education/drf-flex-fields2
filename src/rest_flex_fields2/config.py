"""
Runtime configuration for ``rest_flex_fields2``.

Reads the optional ``REST_FLEX_FIELDS`` dict from Django settings and
exposes validated constants used throughout the package.  Raises
``AssertionError`` or ``ValueError`` on invalid configuration so
errors surface at import time rather than at request time.
"""

from django.conf import settings

FLEX_FIELDS_OPTIONS = getattr(settings, "REST_FLEX_FIELDS", {})
"""Raw ``REST_FLEX_FIELDS`` dictionary from Django settings."""

EXPAND_PARAM = FLEX_FIELDS_OPTIONS.get("EXPAND_PARAM", "expand")
"""Query parameter name used to request expandable fields."""

FIELDS_PARAM = FLEX_FIELDS_OPTIONS.get("FIELDS_PARAM", "fields")
"""Query parameter name used to include only selected fields."""

OMIT_PARAM = FLEX_FIELDS_OPTIONS.get("OMIT_PARAM", "omit")
"""Query parameter name used to omit selected fields."""

MAXIMUM_EXPANSION_DEPTH = FLEX_FIELDS_OPTIONS.get("MAXIMUM_EXPANSION_DEPTH", None)
"""Maximum nested expansion depth. ``None`` means unlimited."""

RECURSIVE_EXPANSION_PERMITTED = FLEX_FIELDS_OPTIONS.get("RECURSIVE_EXPANSION_PERMITTED", True)
"""Whether recursive field expansion is allowed."""

WILDCARD_ALL = "~all"
"""Wildcard token that expands all fields."""

WILDCARD_ASTERISK = "*"
"""Wildcard token alternative that expands all fields."""

if "WILDCARD_EXPAND_VALUES" in FLEX_FIELDS_OPTIONS:
    wildcard_values = FLEX_FIELDS_OPTIONS["WILDCARD_EXPAND_VALUES"]
elif "WILDCARD_VALUES" in FLEX_FIELDS_OPTIONS:
    wildcard_values = FLEX_FIELDS_OPTIONS["WILDCARD_VALUES"]
else:
    wildcard_values = [WILDCARD_ALL, WILDCARD_ASTERISK]

WILDCARD_VALUES = wildcard_values
"""Allowed wildcard tokens for expansion, configurable via Django settings."""

assert isinstance(EXPAND_PARAM, str), "'EXPAND_PARAM' should be a string"
assert isinstance(FIELDS_PARAM, str), "'FIELDS_PARAM' should be a string"
assert isinstance(OMIT_PARAM, str),   "'OMIT_PARAM' should be a string"

if not isinstance(WILDCARD_VALUES, (list, type(None))):
    raise ValueError("'WILDCARD_EXPAND_VALUES' should be a list of strings or None")

if not isinstance(MAXIMUM_EXPANSION_DEPTH, (int, type(None))):
    raise ValueError("'MAXIMUM_EXPANSION_DEPTH' should be a int or None")

if not isinstance(RECURSIVE_EXPANSION_PERMITTED, bool):
    raise ValueError("'RECURSIVE_EXPANSION_PERMITTED' should be a bool")
