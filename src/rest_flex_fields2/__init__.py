"""
Public API for the ``rest_flex_fields2`` package.

Exports configuration constants, the main serializer mixin and model
serializer, the convenience view set, and the request-inspection helpers
`is_expanded` and `is_included`.
"""

from .config import (
    EXPAND_PARAM,
    FIELDS_PARAM,
    FLEX_FIELDS_OPTIONS,
    MAXIMUM_EXPANSION_DEPTH,
    OMIT_PARAM,
    RECURSIVE_EXPANSION_PERMITTED,
    WILDCARD_ALL,
    WILDCARD_ASTERISK,
    WILDCARD_VALUES,
)

from . import utils
from .serializers import FlexFieldsModelSerializer
from .views import FlexFieldsModelViewSet
from .utils import is_expanded, is_included

__all__ = [
    "EXPAND_PARAM",
    "FIELDS_PARAM",
    "FLEX_FIELDS_OPTIONS",
    "MAXIMUM_EXPANSION_DEPTH",
    "OMIT_PARAM",
    "RECURSIVE_EXPANSION_PERMITTED",
    "WILDCARD_ALL",
    "WILDCARD_ASTERISK",
    "WILDCARD_VALUES",
    "FlexFieldsModelSerializer",
    "FlexFieldsModelViewSet",
    "is_expanded",
    "is_included",
]
