""" Utility helpers for ``rest_flex_fields2``.

Provides request-inspection functions (`is_expanded`, `is_included`) and
the `split_levels` helper that partitions dot-notation field lists into
current-level and next-level fragments.
"""

from collections.abc import Iterable

from .config import EXPAND_PARAM, FIELDS_PARAM, OMIT_PARAM, WILDCARD_VALUES


def is_expanded(request, field: str) -> bool:
    """ Return whether `field` is requested for expansion.

    Inspects the ``expand`` query parameter on `request`.  Returns
    ``True`` when `field` appears in the comma-separated expand list, or
    when a wildcard value (e.g. ``*`` or ``~all``) is present.
    """
    expand_value = request.query_params.get(EXPAND_PARAM)
    expand_fields = []

    if expand_value:
        for f in expand_value.split(","):
            expand_fields.extend([_ for _ in f.split(".")])

    wildcard_values = WILDCARD_VALUES or []
    return any(field for field in expand_fields if field in wildcard_values) or field in expand_fields


def is_included(request, field: str) -> bool:
    """ Return whether `field` should be included in the response.

    Returns ``False`` when the ``fields`` sparse-fieldset parameter is
    present and `field` is not listed, or when the ``omit`` parameter is
    present and `field` is listed.  Returns ``True`` otherwise.
    """
    sparse_value = request.query_params.get(FIELDS_PARAM)
    omit_value = request.query_params.get(OMIT_PARAM)
    sparse_fields, omit_fields = [], []

    if sparse_value:
        for f in sparse_value.split(","):
            sparse_fields.extend([_ for _ in f.split(".")])

    if omit_value:
        for f in omit_value.split(","):
            omit_fields.extend([_ for _ in f.split(".")])

    if len(sparse_fields) > 0 and field not in sparse_fields:
        return False

    if len(omit_fields) > 0 and field in omit_fields:
        return False

    return True


def split_levels(
    fields: str | Iterable[str],
) -> tuple[list[str], dict[str, list[str]]]:
    """Split a dot-notation field list into current-level and next-level parts.

    Given an iterable such as ``['a', 'a.b', 'a.d', 'c']``, returns a
    tuple ``(first_level, next_level)`` where ``first_level`` is the
    deduplicated list of top-level names (e.g. ``['a', 'c']``) and
    ``next_level`` is a dict mapping each name to its remaining path
    fragments (e.g. ``{'a': ['b', 'd']}``).  A plain string is treated
    as a comma-separated field list.
    """
    first_level_fields: list[str] = []
    next_level_fields: dict[str, list[str]] = {}

    if not fields:
        return first_level_fields, next_level_fields

    assert isinstance(
        fields, Iterable
    ), "`fields` must be iterable (e.g. list, tuple, or generator)"

    if isinstance(fields, str):
        fields = [a.strip() for a in fields.split(",") if a.strip()]
    for e in fields:
        if "." in e:
            first_level, next_level = e.split(".", 1)
            first_level_fields.append(first_level)
            next_level_fields.setdefault(first_level, []).append(next_level)
        else:
            first_level_fields.append(e)

    first_level_fields = list(set(first_level_fields))
    return first_level_fields, next_level_fields
