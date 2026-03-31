"""
    This class helps provide control over which fields can be expanded when a
    collection is request via the list method.
"""

from typing import Any
from rest_framework import viewsets


class FlexFieldsMixin:
    permit_list_expands = []
    action:            str | None = None

    def get_serializer_context(self) -> dict[str, Any]:
        default_context = super().get_serializer_context()  # type: ignore[misc]

        if hasattr(self, "action") and self.action == "list":
            default_context["permitted_expands"] = self.permit_list_expands

        return default_context


class FlexFieldsModelViewSet(FlexFieldsMixin, viewsets.ModelViewSet):
    pass

