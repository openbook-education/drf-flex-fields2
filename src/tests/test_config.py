"""Unit tests for configuration loading and validation in ``rest_flex_fields2.config``."""

import importlib

from django.test import SimpleTestCase, override_settings


class ConfigModuleTests(SimpleTestCase):
    """Tests for runtime configuration parsing and validation branches."""

    def setUp(self):
        """Store the original config module state."""
        import rest_flex_fields2.config as config_module

        self._original_config = importlib.reload(config_module)

    def tearDown(self):
        """Restore the config module to default state after each test."""
        import rest_flex_fields2.config as config_module

        importlib.reload(config_module)

    @staticmethod
    def _reload_config_module():
        """Reload and return the config module so settings are re-evaluated."""
        import rest_flex_fields2.config as config_module

        return importlib.reload(config_module)

    @override_settings(REST_FLEX_FIELDS2={"WILDCARD_EXPAND_VALUES": ["all"]})
    def test_wildcard_expand_values_are_preferred_when_present(self):
        """``WILDCARD_EXPAND_VALUES`` takes precedence over legacy wildcard keys."""
        config_module = self._reload_config_module()
        self.assertEqual(config_module.WILDCARD_VALUES, ["all"])

    @override_settings(
        REST_FLEX_FIELDS2={
            "WILDCARD_EXPAND_VALUES": ["all"],
            "WILDCARD_VALUES": ["ignored"],
        }
    )
    def test_wildcard_expand_values_have_priority_over_wildcard_values(self):
        """When both keys exist, ``WILDCARD_EXPAND_VALUES`` wins."""
        config_module = self._reload_config_module()
        self.assertEqual(config_module.WILDCARD_VALUES, ["all"])

    @override_settings(REST_FLEX_FIELDS2={"WILDCARD_VALUES": ["legacy"]})
    def test_wildcard_values_are_used_when_expand_values_are_missing(self):
        """Legacy ``WILDCARD_VALUES`` is used when expand-values key is absent."""
        config_module = self._reload_config_module()
        self.assertEqual(config_module.WILDCARD_VALUES, ["legacy"])

    @override_settings(REST_FLEX_FIELDS2={"WILDCARD_VALUES": "not-a-list"})
    def test_invalid_wildcard_values_type_raises_value_error(self):
        """Non-list wildcard values are rejected at import time."""
        with self.assertRaises(ValueError):
            self._reload_config_module()

    @override_settings(REST_FLEX_FIELDS2={"MAXIMUM_EXPANSION_DEPTH": "3"})
    def test_invalid_maximum_expansion_depth_type_raises_value_error(self):
        """Non-integer expansion-depth settings are rejected."""
        with self.assertRaises(ValueError):
            self._reload_config_module()

    @override_settings(REST_FLEX_FIELDS2={"RECURSIVE_EXPANSION_PERMITTED": "yes"})
    def test_invalid_recursive_expansion_permitted_type_raises_value_error(self):
        """Non-boolean recursive-expansion settings are rejected."""
        with self.assertRaises(ValueError):
            self._reload_config_module()
