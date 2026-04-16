GitHub Development Process
==========================

This page describes the expected repository workflow from issue triage to merge.

Issue to branch
---------------

1. Confirm scope and expected behavior in an issue.
2. Create a feature branch from ``main`` (ideally from within the GitHub issue).
3. Keep branch changes focused to one logical change.

Suggested branch naming (note, that this requires manually changing the
suggested branch name when creating the branch within an issue):

- ``<issue>/feature/<short-description>``
- ``<issue>/bugfix/<short-description>``
- ``<issue>/docs/<short-description>``
- ``<issue>/quality/<short-description>``
- …

Pull request
------------

1. Link relevant issue in the PR description. Ideally open an issue, first.
2. Describe behavior changes and optionally test coverage, if not obvious from the issue.
3. Add or update documentation for user-facing changes.
4. Update :doc:`/reference/changelog` for notable user-facing updates.
5. Try to keep test coverage at or above **90%** (the CI workflow will fail otherwise).

Checks and review
-----------------

- Required CI checks must pass.
- The ``tests`` status check from ``.github/workflows/run-tests.yml`` is the
  required branch protection check.
- For relevant code changes, full compatibility tests run through ``poetry run
  nox`` across the Django/DRF dependency matrix.
- The full test workflow executes for each supported Python version.
- For non-relevant changes, the dummy workflow path is used to satisfy branch
  protection without running the full suite.
- Coverage checks must remain at or above the configured threshold.
- Copilot review is requested automatically.
- Manual maintainer review confirms behavior, tests, and documentation quality.

Review focus areas:

- Correctness and regression risk
- Test completeness
- API/documentation consistency
- Clarity and maintainability

Runtime dependency update flow
------------------------------

Runtime dependency updates (Django, Django REST Framework, Python support line)
are handled manually from Renovate's Dependency Dashboard issue or draft PRs.

For each runtime update cycle:

1. Update constraints in ``pyproject.toml``.
2. Update Django/DRF test bounds in ``noxfile.py``.
3. Update the Python CI matrix in ``.github/workflows/run-tests-full.yml``.
4. Update classifiers in ``pyproject.toml`` where needed.
5. Run tests and documentation checks, then open a PR.

Release handoff
---------------

The step-by-step release checklist (version bump, tagging, PyPI publish) is in
:doc:`/maintainers/versioning-and-releases`. Repository-level and external
service configuration is documented in :doc:`/maintainers/repository-setup`.
