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

Pull request expectations
-------------------------

1. Link relevant issue in the PR description. Ideally open an issue, first.
2. Describe behavior changes and optionally test coverage, if not obvious from the issue.
3. Add or update documentation for user-facing changes.
4. Update :doc:`/reference/changelog` for notable user-facing updates.
5. Try to keep test coverage at or above **90%** (the CI workflow will fail otherwise).

Checks and review
-----------------

- Required CI checks must pass.
- Coverage checks must remain at or above the configured threshold.
- Copilot review is requested automatically.
- Manual maintainer review confirms behavior, tests, and documentation quality.

Review focus areas:

- Correctness and regression risk
- Test completeness
- API/documentation consistency
- Clarity and maintainability

Merge and follow-up
-------------------

1. Merge after review conditions are satisfied.
2. Delete merged branch.
3. Verify release notes/changelog coverage before the next release.

Release handoff
---------------

Publishing and external setup details are documented in
:doc:`/maintainers/repository-setup`.
