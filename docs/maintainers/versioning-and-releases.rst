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
version of 2 to reflect the modernized tooling, updated minimum requirements,
and forked lineage — not because the user-facing API was broken, except for
import path changes.

Release Checklist
-----------------

1. **Ensure main is green.**

   All CI checks must pass before tagging.

2. **Create release issue (recommended).**

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
   See :ref:`changelog-format` below for the expected format.

6. **Bump the version number** in ``pyproject.toml`` using Poetry:

   .. code-block:: bash

      # choose one of: patch, minor, major
      poetry version minor

7. **Commit the version bump:**

   .. code-block:: bash

      git add pyproject.toml docs/reference/changelog.rst
      git commit -m "Bump version: vX.Y.Z"

8. **Open and merge pull request.**

   Now open a pull request to merge the release preparation branch into main. At this
   stage Copilot will review the branch, code quality and security will be scanned,
   documentation will be built, and unit tests will run. Usually you will need to
   push a few more commits to the release branch (which will automatically appear in
   the PR and retrigger quality checks).

   Once all is green, merge the pull request into main.

9. **Tag the commit in order to trigger the release workflow.**

   Checkout the main branch and tag the merge commit, then push the tag to GitHub:

   .. code-block:: bash

      git checkout main
      git pull
      git tag vX.Y.Z
      git push origin --tags

   The ``.github/workflows/release.yml`` workflow will automatically:

   - Verify the tag version matches ``pyproject.toml``
   - Run the full test suite and build the documentation again (for safety)
   - Build source distribution (``.tar.gz``) and wheel (``.whl``) artifacts
   - Generate a CycloneDX SBOM (``sbom.cyclonedx.json``)
   - Create a GitHub release with release notes extracted from the changelog
   - Publish the package to PyPI

   Monitor the workflow run in the **Actions** tab.

.. _changelog-format:

Changelog Format
----------------

The changelog is located in ``docs/reference/changelog.rst`` and uses
reStructuredText (RST) formatting. Each version entry must follow this structure,
allowing the release workflow to extract the changelog entries for the GitHub
release page.

.. code-block:: rst

   X.Y.Z (Month Year)
   ^^^^^^^^^^^^^^^^^^

   - Change 1
   - Change 2
   - Change 3

**Guidelines:**

- Use the exact version number (e.g., ``2.1.0``) without the ``v`` prefix.
- Add the release date in parentheses (e.g., ``(April 2025)``).
- Add underline using ``^`` characters of same length.
- List changes as bullet points with clear, user-facing descriptions.
- Start descriptions with the affected component (e.g., "Fixed bug in
  ``FlexFieldsFilterBackend``...").
- Group related changes together logically.

**Pre-releases:**

For pre-release versions (alpha, beta, release candidate), use the extended
version format in the tag and changelog:

.. code-block:: bash

   git tag v2.1.0-pre1
   git tag v2.1.0-rc1

Update the changelog accordingly:

.. code-block:: rst

   2.1.0-pre1 (April 2025)
   ^^^^^^^^^^^^^^^^^^^^^^

   - Preview of upcoming features...

The release workflow will automatically detect pre-releases and mark them as
such in GitHub.

Read the Docs
-------------

Documentation is rebuilt automatically on every push to ``main`` and on every
tag that matches the ``v*`` pattern. No manual trigger is needed after pushing
a release tag. See :doc:`/maintainers/repository-setup` for details of the Read
the Docs project settings and automation rules.
