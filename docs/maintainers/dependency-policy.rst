Dependency Policy
=================

This page documents how ``drf-flex-fields2`` manages dependency updates.

.. contents::
   :local:
   :depth: 1

Runtime Dependencies
--------------------

``drf-flex-fields2`` is intentionally small. At runtime we only rely on:

- Django
- Django REST Framework

No other runtime dependencies are required.

Because this project is a reusable library rather than an application, we keep
runtime ranges deliberately wide and only define minimum versions.

Open ranges for runtime dependencies
------------------------------------

Since Django and Django REST Framework are imported in the library code, they
are treated as runtime dependencies under Python packaging best practices.

The minimum versions are tracked by policy:

- Django ``>=`` most recent LTS release
- Django REST Framework ``>=`` major release from about one year ago
- Python: last three versions

For Django REST Framework, the second segment (for example the ``16`` in
``3.16``) is treated as the effective major line for compatibility planning,
because the first segment changes infrequently.

No upper bounds are set for runtime dependencies. The default expectation is
forward compatibility with newer Django and Django REST Framework releases. If
an upstream release introduces an incompatibility, we detect it proactively
through CI and release a compatibility update.

Non-Runtime Dependencies
------------------------

Development and documentation dependencies are treated differently. They are
not part of the library's public compatibility contract, so we generally bump
them to the most recent available version.

This applies to dependencies such as:

- test and coverage tooling
- Sphinx and documentation extensions
- GitHub Actions dependencies

Automated Updates With Renovate
-------------------------------

`Renovate <https://docs.renovatebot.com/>`_ regularly checks the repository for
dependency updates.

Our Renovate configuration follows these rules:

- Runtime dependencies (Django, Django REST Framework, Python) are tracked in
  the Dependency Dashboard and require manual approval before Renovate may
  create a pull request.
- A dedicated issue (``Runtime dependency updates available``) is automatically
  created or updated whenever pending runtime updates are detected, so maintainers
  do not need to proactively monitor the dashboard.
- Non-runtime Poetry dependencies are grouped and pinned to exact versions,
  then auto-merged after required status checks pass.
- GitHub Actions updates are auto-merged after required status checks pass.

When Renovate opens an auto-merge pull request, the full CI test suite runs
automatically. Auto-merge therefore only happens after repository checks succeed.

Test Strategy For Dependency Updates
------------------------------------

We validate the open ranges with ``nox`` by testing lower and upper tracked
dependency combinations for Django and Django REST Framework, including
cross-combinations:

- min Django + min DRF
- max Django + max DRF
- min Django + max DRF
- max Django + min DRF

In CI, this matrix is executed across the last three supported Python versions.
This reduces the risk of regressions at supported boundaries while still
keeping maintenance manageable.

Manual Maintenance
------------------

When a new major Python version or a new major Django version is released, maintainers
must manually update the Trove classifiers in ``pyproject.toml``.

Renovate can update dependency constraints, but it will not infer or adjust the
package metadata that declares official support.
