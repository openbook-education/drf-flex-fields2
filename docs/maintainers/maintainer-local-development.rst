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
3. Run docs build if public behavior or docs changed.
4. Keep changelog updates in :doc:`/reference/changelog` for user-visible
   changes.
