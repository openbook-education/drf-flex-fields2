""" Flex-fields view mixin and model view set.

Provides `FlexFieldsMixin` for controlling per-action expansion permissions
and the ready-to-use `FlexFieldsModelViewSet` that combines the mixin with
``ModelViewSet`` from Django REST Framework.
"""

from typing import Any
from rest_framework.viewsets import ModelViewSet


class FlexFieldsMixin:
    """ View mixin that restricts which fields may be expanded on list actions.

    Set ``permit_list_expands`` to a list of field names that are allowed to
    be expanded when the view is handling a ``list`` request.  The allowed
    names are passed to the serializer via ``context['permitted_expands']``
    so that `FlexFieldsSerializerMixin` can enforce the constraint.
    """
    permit_list_expands: list[str] = []
    action: str | None = None

    def get_serializer_context(self) -> dict[str, Any]:
        """ Extend the serializer context with ``permitted_expands`` for list actions.

        When the current action is ``list``, adds
        ``context['permitted_expands']`` populated from ``permit_list_expands``
        so the serializer can restrict expansion accordingly.
        """
        default_context = super().get_serializer_context()  # type: ignore[misc]

        if hasattr(self, "action") and self.action == "list":
            default_context["permitted_expands"] = self.permit_list_expands

        return default_context


class FlexFieldsModelViewSet(FlexFieldsMixin, ModelViewSet):
    """ Convenience view set combining `FlexFieldsMixin` with ``ModelViewSet``.

    Drop-in replacement for ``viewsets.ModelViewSet`` with list-action
    expansion control provided by `FlexFieldsMixin`.
    """

