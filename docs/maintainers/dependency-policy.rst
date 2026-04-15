Dependency Policy
=================

This page documents how ``drf-flex-fields2`` manages dependency updates.

.. contents::
   :local:
   :depth: 1

Runtime Dependencies
--------------------

``drf-flex-fields2`` is intentionally small. At runtime it only relies on:

- Django
- Django REST Framework

No other runtime dependencies are required.

Because this project is a reusable library rather than an application, runtime
ranges are kept deliberately wide and only minimum versions are defined.

Open ranges for runtime dependencies
------------------------------------

Since Django and Django REST Framework are imported in the library code, they
are treated as runtime dependencies under Python packaging best practices.

The minimum versions are tracked by policy and currently set to:

- Django ``>=`` most recent LTS release
- Django REST Framework ``>=`` major release from about one year ago
- Python: last three versions

For Django REST Framework, the second segment (for example the ``16`` in
``3.16``) is treated as the effective major line for compatibility planning,
because the first segment changes infrequently.

No upper bounds are set for runtime dependencies. The default expectation is
forward compatibility with newer Django and Django REST Framework releases. If
an upstream release introduces an incompatibility, it is detected proactively
through CI and a compatibility update is published.

Non-Runtime Dependencies
------------------------

Development and documentation dependencies are treated differently. They are
not part of the library's public compatibility contract, so they are generally
bumped to the most recent available version.

This applies to dependencies such as:

- test and coverage tooling
- Sphinx and documentation extensions
- GitHub Actions dependencies

Automated Updates With Renovate
-------------------------------

`Renovate <https://docs.renovatebot.com/>`_ regularly checks the repository for
dependency updates. Renovate is run by ``.github/workflows/run-renovate.yml``
(scheduled weekly and available through manual dispatch). The strategy is:

- Runtime dependencies (Django, Django REST Framework, Python) are tracked as
  manual work through the Dependency Dashboard issue and draft PRs. Maintainers
  perform runtime range and matrix updates manually.
- Non-runtime Poetry dependencies are pinned to exact versions and auto-merged
  after required status checks pass.
- GitHub Actions dependencies are updated and auto-merged after required status
  checks pass.

When Renovate opens an auto-merge pull request, required repository checks must
pass before merge.

Test Strategy For Dependency Updates
------------------------------------

Regular compatibility testing is split across GitHub Actions and ``nox``:

- GitHub Actions runs the workflow for each supported Python version.
- ``nox`` runs the Django/DRF compatibility matrix.

The ``nox`` matrix validates lower and upper tracked combinations for Django
and Django REST Framework, including cross-combinations:

- min Django + min DRF
- max Django + max DRF
- min Django + max DRF
- max Django + min DRF

This reduces the risk of regressions at supported boundaries while still
keeping maintenance manageable. Additionally, the matrix validations can
be run locally with the command ``poetry run nox``.

Manual Maintenance
------------------

When a new supported Python or runtime dependency line is adopted, maintainers
must manually update all affected compatibility declarations, including:

- dependency constraints in ``pyproject.toml``
- Python matrix entries in ``.github/workflows/run-tests-full.yml``
- Django/DRF bounds in ``noxfile.py``
- Trove classifiers in ``pyproject.toml``

Renovate can suggest relevant changes, but it will not infer or safely update
this full compatibility contract automatically.
