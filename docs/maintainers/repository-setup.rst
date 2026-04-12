Repository and Tooling Setup
============================

This document records the repository configuration that was put in place to
keep CI, dependency management, and published documentation working. Some of
that behavior depends on settings outside the repository, so the external setup
is documented here as part of the repository's operational state.

.. contents::
   :local:
   :depth: 1

Repository Secrets
------------------

Under **Settings → Secrets and variables → Actions**, the following repository
secrets were created:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Secret name
     - Description
   * - ``RENOVATE_TOKEN``
     - Fine-grained personal access token for Renovate and SBOM automation.
   * - ``POETRY_PYPI_TOKEN_PYPI``
     - PyPI API token used by the automated release workflow when publishing.

``RENOVATE_TOKEN`` was configured so Renovate and related SBOM automation could
open pull requests and merge auto-mergeable dependency updates after checks
passed.

``POETRY_PYPI_TOKEN_PYPI`` must contain a PyPI token with permission to upload
new releases for ``drf-flex-fields2``. The release workflow passes it straight
through to Poetry, which reads the value from the standard
``POETRY_PYPI_TOKEN_PYPI`` environment variable.

The token belongs to a user with write access to the repository and has the
following permissions:

- Read access to metadata
- Read and write access to code, issues, pull requests, and workflows

Branch Protection Rules
-----------------------

Under **Settings → Rules → Rulesets** or **Settings → Branches**, the
following rules were applied to the default branch.

Require a pull request before merging
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Direct pushes to the default branch were blocked so all changes would go
through pull requests.

The required status check is ``tests``, which is the final aggregator job from
``.github/workflows/run-tests.yml``. That workflow routes changes either to the
full test suite or to the dummy success workflow depending on whether relevant
code changed.

This setup kept branch protection strict for package changes while avoiding
expensive test runs for unrelated repository maintenance.

Automatically request a Copilot code review
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Under **Settings → General → Pull Requests**, *Automatically request Copilot
code review* was enabled.

Allow release automation to push
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The release workflow reuses ``RENOVATE_TOKEN`` for the checkout step. Because
that token belongs to a maintainer account that already has bypass rights on
the default-branch ruleset, the automated release commit and ``vX.Y.Z`` tag
can be pushed directly without any additional ruleset configuration.

No separate bypass entry for GitHub Actions is required. The ``GITHUB_TOKEN``
that GitHub Actions provides by default does not have ruleset bypass rights on
the free plan, which is why the personal access token is used instead.

Read the Docs Project Settings
------------------------------

The repository includes ``.readthedocs.yaml`` and ``docs/conf.py``, but Read
the Docs still required one-time project configuration outside the repository.

The project was configured in Read the Docs with the following settings:

- The GitHub repository was imported into Read the Docs.
- ``main`` was kept as the default branch.
- The Read the Docs GitHub webhook remained enabled so pushes and tags stayed
  synchronized automatically.
- The checked-in ``.readthedocs.yaml`` file was used instead of manually
  configuring build commands in the UI.
- An automation rule was added in **Admin → Automation Rules** or the versions
  UI so release tags would activate automatically.
- For repositories using tags such as ``v2.0.0``, a pattern such as ``v*`` was
  used. A wildcard pattern of ``*`` would only have been appropriate if every
  Git tag was meant to become a published docs version.
- ``latest`` was kept as the default version, and the newest release could be
  promoted to ``stable`` when needed.

No additional GitHub secret is required for tag-triggered Read the Docs builds
because the repository was connected through the native GitHub integration.

Local Development Workflow
--------------------------

Poetry was adopted as the single entry point for local development, tests, and
documentation builds.

Dependencies, including documentation tools, were installed with:

.. code-block:: bash

  poetry install --no-interaction --with docs

Tests were run from the project root with:

.. code-block:: bash

  poetry run python src/manage.py test

Documentation was built locally with:

.. code-block:: bash

  poetry run sphinx-build -W --keep-going docs/ /tmp/sphinx-test-build

The ``docs/`` directory was established as the canonical documentation source
location.

Release, Tagging, and Publishing
--------------------------------

The release process was standardized as follows to keep the package and
documentation in sync:

- Dependency-only updates merged from Renovate pull requests labeled
  ``minor-update`` trigger ``.github/workflows/release-new-version.yml``.
  That workflow bumps the patch version in ``pyproject.toml``, creates a
  ``vX.Y.Z`` tag, pushes both to GitHub, and runs ``poetry publish --build``.
- Manual releases remain available for feature work, documentation-driven
  releases, or any change that requires a deliberate version choice.

1. The version in ``pyproject.toml`` was updated, for example with
   ``poetry version patch`` or ``poetry version 2.1.0``.
2. Release notes were added to ``docs/changelog.rst``.
3. Tests and the documentation build were run locally.
4. The release changes were committed and an annotated tag such as ``v2.1.0``
   was created.
5. The branch and tag were pushed to GitHub with ``git push`` and
   ``git push --tags``.
6. The package was published when required:

   .. code-block:: bash

      poetry build
      poetry publish

With the automation rules above in place, the pushed Git tag triggered the
corresponding Read the Docs version.

Root Configuration Files
------------------------

``pyproject.toml``
^^^^^^^^^^^^^^^^^^

This file was established as the central project configuration managed by
`Poetry <https://python-poetry.org/>`_. It contains:

- Project metadata such as package name, version, authors, and repository URL
- Runtime dependency definitions
- Documentation dependency definitions in
  ``[tool.poetry.group.docs.dependencies]``

``poetry.lock``
^^^^^^^^^^^^^^^

This file was generated by Poetry and committed to the repository so every
environment would resolve identical dependency versions.

``renovate.json5``
^^^^^^^^^^^^^^^^^^

This file was added as the configuration for
`Renovate <https://docs.renovatebot.com/>`_. It manages Poetry and GitHub
Actions dependencies, separates major from minor upgrades, and supports
automated merges for safe updates.

``docs/conf.py``
^^^^^^^^^^^^^^^^

This file serves as the primary Sphinx documentation configuration. It defines
extensions, the sphinx-rtd-theme, autoapi directories, and build options.

``.readthedocs.yaml``
^^^^^^^^^^^^^^^^^^^^^

This file was added as the Read the Docs build configuration. It installs
Poetry after environment creation, overrides the install step to install the
project together with the docs dependency group, and builds the site with
Sphinx.

``docs/``
^^^^^^^^^

This directory was designated as the source location for the documentation
site. It contains the user guide, API reference pages, changelog, and
maintainer notes.

``.github/workflows/build-docs.yml``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This workflow was added to build the Sphinx site in CI on documentation,
packaging, and public API changes. That keeps local docs changes aligned with
what Read the Docs builds.

``.github/workflows/run-tests.yml``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This workflow was added to route pull requests either to the full Django test
suite or to the dummy check, depending on whether relevant code changed.

``.editorconfig``
^^^^^^^^^^^^^^^^^

This file defines editor-wide formatting defaults, including four-space
indentation and LF line endings.

``.gitattributes``
^^^^^^^^^^^^^^^^^^

This file records Git attributes for generated or special-case files.

``.gitignore``
^^^^^^^^^^^^^^

This file defines ignore rules for Python cache directories, virtual
environments, and local build artifacts.
