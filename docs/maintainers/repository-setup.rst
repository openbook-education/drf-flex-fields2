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
secret was created:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Secret name
     - Description
   * - ``RENOVATE_TOKEN``
     - Fine-grained personal access token for the scheduled Renovate workflow.

``RENOVATE_TOKEN`` is used by ``.github/workflows/run-renovate.yml`` so
Renovate can open dependency pull requests and update the Dependency Dashboard
issue.

The token belongs to a user with write access to the repository and has the
following permissions:

- Read access to metadata
- Read and write access to code, issues, pull requests, and workflows

PyPI Trusted Publisher (OIDC)
-----------------------------

Instead of using long-lived API tokens, the release workflow uses `PyPI's OIDC
Trusted Publisher <https://docs.pypi.org/trusted-publishers/>`_ feature to
securely publish packages to PyPI without storing credentials in repository
secrets.

To set up the trusted publisher:

1. Log in to `PyPI <https://pypi.org/>`_ with an account that has admin access
   to the ``drf-flex-fields2`` project.

2. Navigate to the project settings and select **Publishing** or **Trusted
   publishers**.

3. Click **Add a new trusted publisher** and configure it as follows:

   - **Publisher name**: `GitHub`
   - **Repository owner**: `openbook-education`
   - **Repository name**: `drf-flex-fields2`
   - **Workflow name**: `release.yml`
   - **Environment name**: (leave blank or use default)

4. Confirm and save the configuration.

Once configured, the ``.github/workflows/release.yml`` workflow will
authenticate to PyPI using OpenID Connect (OIDC) and can publish packages
without any API tokens stored in the repository.

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

CI Workflows
------------

The repository currently uses a small workflow set:

- ``.github/workflows/run-tests.yml``: Entry workflow to run the test suite
  depending on which files have changed – either the full test suite or a
  lightweight dummy test workflow.
- ``.github/workflows/run-tests-full.yml``: Full test and coverage run across
  the supported Python matrix.
- ``.github/workflows/run-tests-dummy.yml``: Lightweight success path for
  pull requests without relevant Python/package/workflow changes.
- ``.github/workflows/run-renovate.yml``: Weekly and on-demand Renovate run.
- ``.github/workflows/build-docs.yml``: Builds documentation on changes to
  the documentation source or public API.
- ``.github/workflows/release.yml``: Automatically publishes releases to PyPI
  when a version tag (e.g., ``v2.0.0``) is pushed to the default branch. See
  :doc:`/maintainers/versioning-and-releases` for details.

Automatically request a Copilot code review
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Under **Settings → General → Pull Requests**, *Automatically request Copilot
code review* was enabled.

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

Root Configuration Files
------------------------

``pyproject.toml``
^^^^^^^^^^^^^^^^^^

This file is the central project configuration managed by
`Poetry <https://python-poetry.org/>`_. It contains:

- Project metadata such as package name, version, authors, and repository URL
- Runtime dependency definitions
- Documentation dependency definitions in
  ``[tool.poetry.group.docs.dependencies]``

``poetry.lock``
^^^^^^^^^^^^^^^

This file is generated by Poetry and committed to the repository so every
environment would resolve identical dependency versions.

``renovate.json5``
^^^^^^^^^^^^^^^^^^

This file is the configuration for
`Renovate <https://docs.renovatebot.com/>`_. It manages Poetry and GitHub
Actions dependencies and supports auto-merging for non-runtime updates after
required checks pass. Runtime dependency updates are tracked for manual
maintenance.

``docs/conf.py``
^^^^^^^^^^^^^^^^

This file serves as the primary Sphinx documentation configuration. It defines
extensions, the sphinx-rtd-theme, autoapi directories, and build options.

``.readthedocs.yaml``
^^^^^^^^^^^^^^^^^^^^^

This file is the Read the Docs build configuration. It installs
Poetry after environment creation, overrides the install step to install the
project together with the docs dependency group, and builds the site with
Sphinx.

``docs/``
^^^^^^^^^

This directory is the source location for the documentation
site. It contains the user guide, API reference pages, changelog, and
maintainer notes.

``.github/workflows/build-docs.yml``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This workflow builds the Sphinx site in CI on documentation,
packaging, and public API changes. That keeps local docs changes aligned with
what Read the Docs builds.

``.github/workflows/run-tests.yml``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This workflow routes pull requests either to the full Django test suite or to
the dummy check, depending on whether relevant code changed.

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
