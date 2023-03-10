from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from wallets.models import Wallet, Transaction
from wallets.serializers import WalletSerializer, TransactionSerializer


class WalletViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    GenericViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    lookup_field = "uuid"


class TransactionViewSet(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         GenericViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
