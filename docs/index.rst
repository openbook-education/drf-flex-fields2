drf-flex-fields2
================

What is it?
^^^^^^^^^^^

``drf-flex-fields2`` adds dynamic field expansion, sparse fieldsets, and nested
serializer control to Django REST Framework serializers with a small API surface
and minimal magic.

Whether you are a first-time user, an API consumer, a backend developer, or a
maintainer looking to help, you are in the right place. The goal of this fork is
to keep a practical and well-documented serializer extension healthy, modern,
and friendly to contribute to.

This is a fork of ``drf-flex-fields`` developed and maintained by Robert Singer
between 2018 and 2023. Users, community contributors, and maintainers are warmly
welcome to keep this package useful and maintained.

What this package gives you
^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Expand nested resources on demand with query parameters such as ``?expand=country.states``.
- Return sparse fieldsets with ``?fields=`` or ``?omit=``.
- Reuse serializers instead of maintaining multiple slim variants.
- Keep list endpoints under control with per-view expansion limits.
- Optionally optimize querysets with a dedicated filter backend.

Supported stack
^^^^^^^^^^^^^^^

- Python 3.12 and 3.13
- Django 6.x
- Django REST Framework 3.17+


.. toctree::
   :maxdepth: 1
   :caption: Getting Started

   getting-started/installation
   getting-started/migration
   getting-started/quickstart
   getting-started/core-concepts

.. toctree::
   :maxdepth: 1
   :caption: Guide

   guide/usage
   guide/serializer-options
   guide/advanced

.. toctree::
   :maxdepth: 1
   :caption: Reference

   reference/api-reference
   reference/changelog
   reference/history

.. toctree::
   :maxdepth: 1
   :caption: Maintainers

   maintainers/maintainer-local-development
   maintainers/maintainer-development-process
   maintainers/maintainer-architecture
   maintainers/repository-setup
