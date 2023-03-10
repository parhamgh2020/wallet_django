from django.contrib.auth.models import User
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from .serializers import UserSerializer


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    """
    A viewset for managing users.

    Allows for creating, retrieving, updating, and listing User objects.

    Inherits from:
      - CreateModelMixin: Allows creating a new User object.
      - RetrieveModelMixin: Allows retrieving a specific User object by ID.
      - UpdateModelMixin: Allows updating a specific User object by ID.
      - ListModelMixin: Allows listing all User objects.

    Attributes:
      - serializer_class: The serializer class to use for User objects.
      - queryset: The queryset to use for User objects.
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
