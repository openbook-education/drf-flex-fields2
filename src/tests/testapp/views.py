"""View sets used by the test suite's ``testapp``."""

from rest_framework.viewsets import ModelViewSet

from rest_flex_fields2 import FlexFieldsModelViewSet
from tests.testapp.models import Pet, TaggedItem
from tests.testapp.serializers import PetSerializer, TaggedItemSerializer


class PetViewSet(FlexFieldsModelViewSet):
    """
    API endpoint for testing purposes.
    """

    serializer_class = PetSerializer
    queryset = Pet.objects.all()
    permit_list_expands = ["owner"]


class TaggedItemViewSet(ModelViewSet):
    """View set for ``TaggedItem`` without flex-fields support, used to test the filter backend."""

    serializer_class = TaggedItemSerializer
    queryset = TaggedItem.objects.all()
