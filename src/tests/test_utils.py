"""Unit tests for the ``is_included`` and ``is_expanded`` utility helpers."""

from django.test import TestCase

from rest_flex_fields2 import is_included, is_expanded, WILDCARD_ALL, WILDCARD_ASTERISK
from rest_flex_fields2.utils import split_levels


class MockRequest:
    """Minimal request stub exposing ``query_params`` and ``method``."""

    def __init__(self, query_params=None, method="GET"):
        """Initialize with an optional query params dict and HTTP method string."""
        if query_params is None:
            query_params = {}
        self.query_params = query_params
        self.method = method


class TestUtils(TestCase):
    """Tests for ``is_included`` and ``is_expanded`` with various query-param combinations."""

    def test_should_be_included(self):
        """Field is included when no ``fields`` or ``omit`` params are present."""
        request = MockRequest(query_params={})
        self.assertTrue(is_included(request, "name"))

    def test_should_not_be_included(self):
        """Field listed in ``omit`` is excluded from the response."""
        request = MockRequest(query_params={"omit": "name,address"})
        self.assertFalse(is_included(request, "name"))

    def test_should_not_be_included_and_due_to_omit_and_has_dot_notation(self):
        """Dot-notation ``omit`` value excludes the matching leaf field."""
        request = MockRequest(query_params={"omit": "friend.name,address"})
        self.assertFalse(is_included(request, "name"))

    def test_should_not_be_included_and_due_to_fields_and_has_dot_notation(self):
        """Dot-notation ``fields`` value excludes fields not in the sparse set."""
        request = MockRequest(query_params={"fields": "hobby,address"})
        self.assertFalse(is_included(request, "name"))

    def test_should_be_expanded(self):
        """Field listed in ``expand`` is identified as expanded."""
        request = MockRequest(query_params={"expand": "name,address"})
        self.assertTrue(is_expanded(request, "name"))

    def test_should_not_be_expanded(self):
        """Field absent from the ``expand`` param is not expanded."""
        request = MockRequest(query_params={"expand": "name,address"})
        self.assertFalse(is_expanded(request, "hobby"))

    def test_should_be_expanded_and_has_dot_notation(self):
        """Dot-notation ``expand`` value matches the leaf field name."""
        request = MockRequest(query_params={"expand": "person.name,address"})
        self.assertTrue(is_expanded(request, "name"))

    def test_all_should_be_expanded(self):
        """Wildcard ``~all`` in ``expand`` causes any field to be considered expanded."""
        request = MockRequest(query_params={"expand": WILDCARD_ALL})
        self.assertTrue(is_expanded(request, "name"))

    def test_asterisk_should_be_expanded(self):
        """Wildcard ``*`` in ``expand`` causes any field to be considered expanded."""
        request = MockRequest(query_params={"expand": WILDCARD_ASTERISK})
        self.assertTrue(is_expanded(request, "name"))

    def test_split_levels_with_empty_input(self):
        """Empty input returns empty first-level and next-level structures."""
        first_level, next_level = split_levels([])
        self.assertEqual(first_level, [])
        self.assertEqual(next_level, {})

    def test_split_levels_with_string_input(self):
        """Comma-separated string input is normalized and split by nesting levels."""
        first_level, next_level = split_levels("owner, owner.employer.name, name")
        self.assertEqual(set(first_level), {"owner", "name"})
        self.assertEqual(next_level, {"owner": ["employer.name"]})

    def test_split_levels_with_nested_iterable_input(self):
        """Nested dot-notation values are partitioned into next-level mappings."""
        first_level, next_level = split_levels(["owner.name", "owner.hobbies", "diet"])
        self.assertEqual(set(first_level), {"owner", "diet"})
        self.assertEqual(next_level, {"owner": ["name", "hobbies"]})

    def test_split_levels_deduplicates_first_level_fields(self):
        """Repeated first-level names are deduplicated in the first-level output."""
        first_level, next_level = split_levels(["owner", "owner.name", "owner"])
        self.assertEqual(first_level, ["owner"])
        self.assertEqual(next_level, {"owner": ["name"]})

    def test_split_levels_rejects_non_iterable_input(self):
        """Non-iterable inputs fail fast with an assertion error."""
        with self.assertRaises(AssertionError):
            split_levels(42)
