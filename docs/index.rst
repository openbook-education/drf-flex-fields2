drf-flex-fields2
================

``drf-flex-fields2`` adds dynamic field expansion, sparse fieldsets, and nested
serializer control to Django REST Framework serializers with a small API surface
and minimal magic.

What it gives you
-----------------

- Expand nested resources on demand with query parameters such as ``?expand=country.states``.
- Return sparse fieldsets with ``?fields=`` or ``?omit=``.
- Reuse serializers instead of maintaining multiple slim variants.
- Keep list endpoints under control with per-view expansion limits.
- Optionally optimize querysets with a dedicated filter backend.

Start here
----------

- If you are new to the package, read :doc:`installation` and :doc:`quickstart`.
- If you already know the basics, jump to :doc:`usage` or :doc:`advanced`.
- If you need the code surface, see :doc:`api-reference`.

Supported stack
---------------

- Python 3.12 and 3.13
- Django 6.x
- Django REST Framework 3.17+

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart

.. toctree::
   :maxdepth: 2
   :caption: Guide

   usage
   serializer-options
   advanced

.. toctree::
   :maxdepth: 2
   :caption: Reference

   api-reference
   CHANGELOG

.. toctree::
   :maxdepth: 1
   :caption: Maintainers

   REPOSITORY-SETUP
