Versioning and Releases
=======================

This page documents the versioning strategy and the steps required to cut a
release of ``drf-flex-fields2``.

.. contents::
   :local:
   :depth: 1

Versioning Strategy
-------------------

``drf-flex-fields2`` follows `Semantic Versioning <https://semver.org/>`_
(SemVer). Given a version number ``MAJOR.MINOR.PATCH``:

- **PATCH** is incremented for backwards-compatible bug fixes.
- **MINOR** is incremented for backwards-compatible new features.
- **MAJOR** is incremented for breaking changes to the public API.

There are currently no plans to introduce breaking changes. Users can safely
update to any patch or minor release without modifying their code.

Version Baseline
----------------

Version **2.0.0** of ``drf-flex-fields2`` is feature-equivalent to version
**1.0.2** of the original ``drf-flex-fields`` package. It carries a major
version of 2 to reflect the modernized tooling, updated minimum requirements
(Django 6, DRF 3.17), and forked lineage — not because any user-facing API was
broken, except for the name change.

Release Checklist
-----------------

1. **Ensure main is green.**

   All CI checks must pass before tagging.

2. **Create release issue.**

   Create a new issue for the release and describe remaining work to be done before
   a new version is released. You don't need to repeat the individual release steps.
   Just, what else needs to be done.

3. **Create new branch.**

   From within the release issue create a new release preparation branch. Checkout
   the branch as the next steps must all be performed within that branch.

4. **Complete remaining work.**

   If there is any remaining work to be done (e.g. updating documentation) push the
   changes onto the release preparation branch.

5. **Update the changelog.**

   Add a dated entry to :doc:`/reference/changelog` summarising user-visible changes.

6. **Bump the version number** in ``pyproject.toml`` using Poetry:

   .. code-block:: bash

      # choose one of: patch, minor, major
      poetry version minor

7. **Commit the version bump:**

   .. code-block:: bash

      git add pyproject.toml docs/reference/changelog.rst
      git commit -m "Release vX.Y.Z"

8. **Open and merge pull request.**

   Now open a pull request to merge the release preparation branch into main. At this
   stage Copilot will review the branch, code quality and security will be scanned and
   unit tests will run. Usually you will need to push a few more commits to the release
   branch (which will automatically appear in the PR and retrigger quality checks).

   Once all is green, merge the pull request into main.

9. **Tag the commit** using the ``vX.Y.Z`` naming convention:

   Checkout the main branch and tag the merge commit.

   .. code-block:: bash

      git tag vX.Y.Z
      git push origin main --tags

10. **Build distribution artifacts:**

   .. code-block:: bash

      poetry build

   This creates both a source distribution (``sdist``) and a wheel in the
   ``dist/`` directory. Inspect the output to confirm the expected files are
   present.

11. **Publish to PyPI:**

   .. code-block:: bash

      poetry publish

   You will need a PyPI API token configured locally. Run
   ``poetry config pypi-token.pypi <token>`` once to store it, or set the
   ``POETRY_PYPI_TOKEN_PYPI`` environment variable.

   For the PyPI test environment run:

   .. code-block:: bash

      poetry publish -r testpypi

   The API token must be set with ``poetry config pypi-token.testpypi <token>`` or
   ``POETRY_PYPI_TOKEN_TESTPYPI``, instead.

12. **Verify the release** on PyPI and confirm the package installs cleanly:

    Create a temporary directory and run the following commands to verify the release.

   .. code-block:: bash

      pip install --upgrade drf-flex-fields2
      python -c "import importlib.metadata as im; print(im.version('drf-flex-fields2'))"

Read the Docs
-------------

Documentation is rebuilt automatically on every push to ``main`` and on every
tag that matches the ``v*`` pattern. No manual trigger is needed after pushing
a release tag. See :doc:`/maintainers/repository-setup` for details of the Read
the Docs project settings and automation rules.
