# drf-flex-fields2

`drf-flex-fields2` adds dynamic field expansion, sparse fieldsets, and nested serializer control to Django REST Framework serializers with a small API surface and minimal magic.

## What it gives you

- Expand nested resources on demand with query parameters such as `?expand=country.states`.
- Return sparse fieldsets with `?fields=` or `?omit=`.
- Reuse serializers instead of maintaining multiple slim variants.
- Keep list endpoints under control with per-view expansion limits.
- Optionally optimize querysets with a dedicated filter backend.

## Start here

- If you are new to the package, read [Installation](installation.md) and [Quick Start](quickstart.md).
- If you already know the basics, jump to [Usage](usage.md) or [Advanced Topics](advanced.md).
- If you need the code surface, see [API Reference](api-reference.md).

## Supported stack

- Python 3.12 and 3.13
- Django 6.x
- Django REST Framework 3.17+

## Documentation versions

The published documentation is intended to be hosted on Read the Docs with one version per Git tag. The repository contains the required `.readthedocs.yaml` and `mkdocs.yml` files for Zensical builds; the remaining one-time project configuration is documented in [Repository Setup](REPOSITORY-SETUP.md).
