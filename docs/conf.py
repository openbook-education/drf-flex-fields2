"""Sphinx configuration for drf-flex-fields2 documentation."""

import os
import sys

# Add the package source directory to sys.path so autoapi can find it.
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("../src"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

project = "drf-flex-fields2"
author = "Dennis Schulmeister, Robert Singer"
copyright = "drf-flex-fields2 maintainers"
release = "2.0.0"

extensions = [
    "autoapi.extension",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

autoapi_dirs = ["../src/rest_flex_fields2"]
autoapi_root = "api"
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
]
autoapi_own_page_level = "class"
autoapi_member_order = "bysource"
autoapi_add_toctree_entry = False

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "navigation_depth": 4,
    "titles_only": False,
}

exclude_patterns = ["_build"]
