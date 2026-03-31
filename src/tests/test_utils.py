"""Unit tests for the ``is_included`` and ``is_expanded`` utility helpers."""

from django.test import TestCase

from rest_flex_fields2 import is_included, is_expanded, WILDCARD_ALL, WILDCARD_ASTERISK


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
