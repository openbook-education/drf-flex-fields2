# drf-flex-fields2

[![Package version](https://badge.fury.io/py/drf-flex-fields2.svg)](https://pypi.org/project/drf-flex-fields2/)

Flexible dynamic fields and nested resources for Django REST Framework serializers.

## Documentation

The full documentation is published on Read the Docs: <https://drf-flex-fields2.readthedocs.io/>

Recommended reading paths:

- New users: Installation -> Quick Start -> Core Concepts -> Usage
- API consumers and backend developers: Usage -> Serializer Options -> Advanced Topics
- Maintainers: Maintainer Local Development -> Maintainer GitHub Development Process -> Maintainer Architecture and Design -> Repository and Tooling Setup

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

## License

See [LICENSE.md](LICENSE.md).