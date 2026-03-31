Tooling
=======

We use `poetry` for dependency management. Always use `poetry` commands.

Before running shell commands requiring Python packages, activate the environment: `poetry shell`

Run unit tests with Django from the `src` directory: `manage.py test`

Code Conventions
================

- Use double quotes for strings (single quotes only if needed).
- Use four spaces for indentation (all languages).
- Prefer `from x import y`; use relative imports within the project (`from .models import MyModel`).
- Group imports: standard library, third-party, local; sort alphabetically within groups.
- Separate logical code blocks with one blank line.

Formatting:

- Align `=` in multi-line calls; use spaces around `=`, trailing commas, and a blank line before the call.
- Align dictionary values in multi-line definitions.
- Use type hints.

Docstrings
==========

Follow PEP 257:

- Use `"""..."""` for all public modules, classes, functions, and methods.
- One-line summary in imperative mood, ending with a period.
- Blank line between summary and details.
- Keep concise; document args, returns, side effects if needed.
- No signature repetition.

Docstrings may be omitted only for trivial functions. When in doubt, include a one-liner.

Comments use Markdown; wrap code elements in backticks (e.g. `my_variable`).

Test Driven Development
=======================

All code must be unit-tested.

Workflow:

1. Extend documentation (specification)
2. Write tests
3. Implement until tests pass
4. Run type and quality checks
5. Update documentation if needed

Documentation
=============

Update `doc/` when changing tooling or functionality.