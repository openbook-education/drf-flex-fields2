# drf-flex-fields2

[![Package version](https://badge.fury.io/py/drf-flex-fields2.svg)](https://pypi.org/project/drf-flex-fields2/)

Flexible dynamic fields and nested resources for Django REST Framework serializers.

## Documentation

The full documentation is intended to be published on Read the Docs:

- Hosted docs: <https://drf-flex-fields2.readthedocs.io/>
- Documentation source: [doc/](doc/)
- Maintainer setup notes: [doc/REPOSITORY-SETUP.md](doc/REPOSITORY-SETUP.md)

## Installation

```bash
pip install drf-flex-fields2
```

## Quick Example

```python
from rest_flex_fields2 import FlexFieldsModelSerializer


class StateSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = State
        fields = ("id", "name")


class CountrySerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "name", "population", "states")
        expandable_fields = {
            "states": (StateSerializer, {"many": True}),
        }


class PersonSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Person
        fields = ("id", "name", "country", "occupation")
        expandable_fields = {
            "country": CountrySerializer,
        }
```

Default response:

```json
{
    "id": 142,
    "name": "Jim Halpert",
    "country": 1
}
```

Expanded response for `GET /people/142/?expand=country.states`:

```json
{
    "id": 142,
    "name": "Jim Halpert",
    "country": {
        "id": 1,
        "name": "United States",
        "states": [
            {
                "id": 23,
                "name": "Ohio"
            },
            {
                "id": 2,
                "name": "Pennsylvania"
            }
        ]
    }
}
```

## Highlights

- Expand nested relations with `?expand=`.
- Limit response payloads with `?fields=` and `?omit=`.
- Use dot notation for nested expansion and sparse fieldsets.
- Reuse serializers by passing `expand`, `fields`, and `omit` directly.

## Development

This repository uses Poetry.

- Run tests from the `src` directory with `manage.py test`.
- Build docs locally with `poetry run zensical build`.

## License

See [LICENSE.md](LICENSE.md).