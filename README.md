# drf-flex-fields2

[![Package version](https://badge.fury.io/py/drf-flex-fields2.svg)](https://pypi.org/project/drf-flex-fields2/)

Flexible dynamic fields and nested resources for Django REST Framework serializers.

This project is for people building APIs, people integrating them, and people
maintaining the ecosystem around them. If you are new to flexible serializers,
welcome. If you are evaluating this for production, welcome. If you want to
contribute fixes, docs, tests, or ideas, welcome.

1. [Migration from drf-flex-fields](#migration-from-drf-flex-fields)
1. [Documentation](#documentation)
1. [Installation](#installation)
1. [Quick Example](#quick-example)
1. [Highlights](#highlights)
1. [License](#license)
1. [History](#history)

## Migration from drf-flex-fields

This is a fork of `drf-flex-fields` developed and maintained by Robert Singer
between 2018 and 2023. For more details on why this fork exists, see
[History](#history) below. See the [Migration Guide](https://drf-flex-fields2.readthedocs.io/en/latest/getting-started/migration/)
in the documentation for detailed instructions. The short version is:

1. Upgrade Django and DRF dependencies, if not done already.
2. Install `drf-flex-fields2` instead of `drf-flex-fields`.
3. Fix import paths
4. Rename `REST_FLEX_FIELDS` to `REST_FLEX_FIELDS2` in Django settings.

The `drf-flex-fields2` API is stable and compatible with the original `drf-flex-fields`
package. There are currently no plans to break the existing API. However, if breaking
changes become necessary in the future, they will follow [semantic versioning](https://semver.org/)
guidelines and the major version number will be incremented accordingly.

Users, community contributors, and maintainers are warmly welcome to keep this
package useful and maintained.

## Documentation

The full documentation is published on Read the Docs: <https://drf-flex-fields2.readthedocs.io/>

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

MIT. See [LICENSE.md](LICENSE.md).

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
