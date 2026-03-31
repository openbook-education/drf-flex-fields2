# Serializer Options

Flex-field options can be supplied in three places.

## 1. Query parameters

```text
GET /people?expand=friends.hobbies,employer&omit=age
```

## 2. Serializer constructor keyword arguments

```python
serializer = PersonSerializer(
    person,
    expand=["friends.hobbies", "employer"],
    omit=["friends.age"],
)
```

## 3. Nested serializer settings in `expandable_fields`

```python
class PersonSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Person
        fields = ["age", "hobbies", "name"]
        expandable_fields = {
            "friends": (
                "serializer.FriendSerializer",
                {"many": True, "expand": ["hobbies"], "omit": ["age"]},
            ),
        }
```

## Supported options

| Option | Description |
| --- | --- |
| `expand` | Fields to expand. They must be configured in `expandable_fields`. |
| `fields` | Fields to include. All other fields are excluded. |
| `omit` | Fields to exclude. All other fields are included. |

Query-parameter values accept comma-separated lists. Nested paths use dot notation.
