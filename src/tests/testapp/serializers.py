"""Serializers used by the test suite's ``testapp``."""

from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from rest_flex_fields2 import FlexFieldsModelSerializer
from tests.testapp.models import Pet, PetStore, Person, Company, TaggedItem


class CompanySerializer(FlexFieldsModelSerializer):
    """Serializer for ``Company`` with ``name`` and ``public`` fields."""

    class Meta:
        model = Company
        fields = ["name", "public"]


class PersonSerializer(FlexFieldsModelSerializer):
    """Serializer for ``Person`` with an expandable ``employer`` relation."""

    class Meta:
        model = Person
        fields = ["name", "hobbies"]
        expandable_fields = {"employer": "tests.testapp.serializers.CompanySerializer"}


class PetStoreSerializer(serializers.ModelSerializer):
    """Plain (non-flex) serializer for ``PetStore``, used as an expandable target."""

    class Meta:
        model = PetStore
        fields = ["id", "name"]


class PetSerializer(FlexFieldsModelSerializer):
    """Serializer for ``Pet`` with expandable ``owner``, ``sold_from``, and ``diet`` fields."""

    owner = serializers.PrimaryKeyRelatedField(queryset=Person.objects.all())
    sold_from = serializers.PrimaryKeyRelatedField(
        queryset=PetStore.objects.all(), allow_null=True
    )
    diet = serializers.CharField()

    class Meta:
        model = Pet
        fields = ["owner", "name", "toys", "species", "diet", "sold_from"]

        expandable_fields = {
            "owner": "tests.testapp.PersonSerializer",
            "sold_from": "tests.testapp.PetStoreSerializer",
            "diet": serializers.SerializerMethodField,
        }

    def get_diet(self, obj):
        """Return a diet description based on the pet's name."""
        if obj.name == "Garfield":
            return "homemade lasanga"
        return "pet food"


class TaggedItemSerializer(FlexFieldsModelSerializer):
    """Serializer for ``TaggedItem`` exposing the generic ``content_object`` relation."""

    content_object = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = TaggedItem
        fields = (
            "id",
            "content_type",
            "object_id",
            "content_object"
        )
