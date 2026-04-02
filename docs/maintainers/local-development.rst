Local Development
=================

This page documents day-to-day local workflows for maintainers.
Repository-level and external service setup remains in
:doc:`/maintainers/repository-setup`.

Prerequisites
-------------

- Python 3.12 or 3.13
- Poetry

Install dependencies
--------------------

.. code-block:: bash

   poetry install --no-interaction --with docs

Run tests
---------

Run the full suite:

.. code-block:: bash

   poetry run python src/manage.py test

Run a specific test module:

.. code-block:: bash

   poetry run python src/manage.py test tests.test_serializer

Run a single test case:

.. code-block:: bash

   poetry run python src/manage.py test tests.test_serializer.YourTestCase

Run test coverage
-----------------

Coverage is configured in ``pyproject.toml`` and enforced with a
``fail_under`` threshold of **90%**.

Run coverage from the repository root:

.. code-block:: bash

   export PYTHONPATH=src
   poetry run coverage run --rcfile=pyproject.toml src/manage.py test tests
   poetry run coverage report --rcfile=pyproject.toml -m

If coverage fails, review the ``Missing`` column and add tests for the
reported lines or branches before opening a PR.

Build documentation
-------------------

.. code-block:: bash

   poetry run sphinx-build -W --keep-going docs/ site/

Common maintenance commands
---------------------------

- Show dependency graph: ``poetry show --tree``
- Update lock file after dependency changes: ``poetry lock``
- Bump package version: ``poetry version patch`` (or ``minor`` / ``major``)

Daily checklist
---------------

1. Pull latest ``main``.
2. Run tests.
3. Run coverage and confirm it stays at or above 90%.
4. Run docs build if public behavior or docs changed.
5. Keep changelog updates in :doc:`/reference/changelog` for user-visible
   changes.
