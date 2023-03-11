from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer


class WalletViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    GenericViewSet):
    """
    A viewset that provides operations for Wallet objects.

    Inherits from CreateModelMixin, RetrieveModelMixin, UpdateModelMixin,
    ListModelMixin, and GenericViewSet. The viewset supports the following
    actions:

    - create: create a new Wallet object.
    - retrieve: retrieve an existing Wallet object by its UUID.
    - update: update an existing Wallet object by its UUID.
    - partial_update: partially update an existing Wallet object by its UUID.
    - list: list all existing Wallet objects.

    The queryset attribute is set to Wallet.objects.all() and the
    serializer_class attribute is set to WalletSerializer. The lookup field
    is "uuid".
    """
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    lookup_field = "uuid"


class TransactionViewSet(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         GenericViewSet):
    """
    A viewset that provide operations for Transaction objects.

    Inherits from CreateModelMixin, RetrieveModelMixin, ListModelMixin, and
    GenericViewSet. The viewset supports the following actions:

    - create: create a new Transaction object.
    - retrieve: retrieve an existing Transaction object by its ID.
    - list: list all existing Transaction objects.

    The queryset attribute is set to Transaction.objects.all() and the
    serializer_class attribute is set to TransactionSerializer.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
