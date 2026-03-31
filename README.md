# drf-flex-fields2

[![Package version](https://badge.fury.io/py/drf-flex-fields2.svg)](https://pypi.org/project/drf-flex-fields2/)

Flexible dynamic fields and nested resources for Django REST Framework serializers.

This project is for people building APIs, people integrating them, and people
maintaining the ecosystem around them. If you are new to flexible serializers,
welcome. If you are evaluating this for production, welcome. If you want to
contribute fixes, docs, tests, or ideas, welcome.

This is a fork of `drf-flex-fields` developed and maintained by Robert Singer
between 2018 and 2023. For more details why this fork exists, see
[History](#history) below.

Users, community contributors, and maintainers are warmly welcome to keep this
package useful and maintained.

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

## History

The original `drf-flex-fields` was developed and maintained by Robert Singer
between 2018 and 2023. However, in 2023 maintenance appeared to stop with no
further commits and issues and pull-requests remaining unanswered.

In March 2026, Django REST Framework 3.17.0 removed coreapi support, which
unfortunately broke the existing package. Although the immediate fix was
simple, the project was due for broader modernization, including tooling updates,
Python 2 to 3 cleanup, dependency version maintenance and proper documentation.

This fork exists because `drf-flex-fields` is used in the
[OpenBook project](https://github.com/openbook-education/openbook), and we want to
reduce supply-chain risk from outdated dependencies while keeping this
package healthy and maintained. Please join the community and help us with
this mission. Oh, and keep your own packages up to date and maintained, will
you? :-)