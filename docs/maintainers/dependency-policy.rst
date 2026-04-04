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

Because this project is a reusable library rather than an application, we do
not pin runtime dependencies to a single tested version. Instead, we keep
version ranges that aim to support the previous major release up to the most
recent tested release.

In practice this means:

- Django is maintained as a major-version window, for example ``>=5.0,<=6.0.3``.
- Django REST Framework follows the same compatibility goal, but is managed a
  little more conservatively because its minor and patch releases are not
  always semver-safe.

This strategy reduces friction for downstream users, who may already be on a
slightly older supported stack version.

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
dependency updates and opens pull requests.

Our Renovate configuration follows these rules:

- Runtime dependencies managed by Poetry use a widening strategy rather than
  simply bumping minimum versions.
- Non-runtime dependencies are grouped and bumped to the newest version.
- Minor and patch updates are configured for automerge when the required status
  checks pass.
- Major version updates always require manual review and are never auto-merged.

When Renovate opens a pull request, the full CI test suite runs automatically.
Automerge therefore only happens after the repository checks succeed.

Test Strategy For Dependency Updates
------------------------------------

The ideal setup for a reusable library would be a full test matrix across
multiple Python, Django, and Django REST Framework combinations.

For pragmatic reasons, this project currently tests only against:

- the most recent supported Python version
- the most recent supported Django version
- the most recent supported Django REST Framework version

This keeps maintenance overhead low and gives fast feedback for Renovate pull
requests. The tradeoff is that there is a small chance of accidentally breaking
older supported dependency versions. Given the limited scope and size of this
project, that risk is considered acceptable.

Manual Maintenance
------------------

When a new Python version or a new major Django version is released, maintainers
must manually update the Trove classifiers in ``pyproject.toml``.

Renovate can update dependency constraints, but it will not infer or adjust the
package metadata that declares official support.
