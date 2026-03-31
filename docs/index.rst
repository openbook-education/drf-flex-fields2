drf-flex-fields2
================

``drf-flex-fields2`` adds dynamic field expansion, sparse fieldsets, and nested
serializer control to Django REST Framework serializers with a small API surface
and minimal magic.

Documentation map by audience
-----------------------------

- New to the package: start with :doc:`/getting-started/installation`, then
   :doc:`/getting-started/quickstart`, then
   :doc:`/getting-started/core-concepts`.
- Building production API endpoints: continue with :doc:`/guide/usage`,
   :doc:`/guide/serializer-options`, and :doc:`/guide/advanced`.
- Maintaining the project: use :doc:`/maintainers/maintainer-local-development`,
   :doc:`/maintainers/maintainer-development-process`, and
   :doc:`/maintainers/maintainer-architecture`.

What it gives you
-----------------

- Expand nested resources on demand with query parameters such as ``?expand=country.states``.
- Return sparse fieldsets with ``?fields=`` or ``?omit=``.
- Reuse serializers instead of maintaining multiple slim variants.
- Keep list endpoints under control with per-view expansion limits.
- Optionally optimize querysets with a dedicated filter backend.

Start here
----------

- If you are new to the package, read :doc:`/getting-started/installation` and
   :doc:`/getting-started/quickstart`.
- If you already know the basics, jump to :doc:`/guide/usage` or
   :doc:`/guide/advanced`.
- If you need the code surface, see :doc:`/reference/api-reference`.

Supported stack
---------------

- Python 3.12 and 3.13
- Django 6.x
- Django REST Framework 3.17+

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   getting-started/installation
   getting-started/quickstart
   getting-started/core-concepts

.. toctree::
   :maxdepth: 2
   :caption: Guide

   guide/usage
   guide/serializer-options
   guide/advanced

.. toctree::
   :maxdepth: 2
   :caption: Reference

   reference/api-reference
   reference/changelog

.. toctree::
   :maxdepth: 1
   :caption: Maintainers

   maintainers/maintainer-local-development
   maintainers/maintainer-development-process
   maintainers/maintainer-architecture
   maintainers/repository-setup
