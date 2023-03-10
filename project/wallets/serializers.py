from datetime import timedelta, datetime

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers

from .models import Wallet, Transaction
from .scheduler import define_schedule_job


class UserSerializer(serializers.ModelSerializer):
    """
    The `UserSerializer` class is a standard `ModelSerializer` for the `User` model,
    with all fields included.
    """
    class Meta:
        model = User
        fields = '__all__'


class WalletSerializer(serializers.HyperlinkedModelSerializer):
    """
    The `WalletSerializer` class is a `HyperlinkedModelSerializer` for the `Wallet`
    model, with the `balance` and `owner` fields included. The `balance` field
    represents the current balance of the wallet, while the `owner` field represents
    the user who owns the wallet. The `owner` field is a nested `UserSerializer`,
    which includes all fields for the `User` model.
    """
    class Meta:
        model = Wallet
        fields = [
            'balance',
            'owner',
        ]


class ChoicesField(serializers.ChoiceField):

    def to_representation(self, value):
        return self.choices.get(value)


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Transaction model.

    The `TransactionSerializer` class specifies the serialization and
    deserialization behavior for the `Transaction` objects when they are
    converted to/from JSON format. It includes validation for the
    `scheduled_time` field and defines the behavior for saving a
    `Transaction` object.
    """

    status = ChoicesField(Transaction.Status.choices, read_only=True)
    method = ChoicesField(Transaction.Method.choices)

    class Meta:
        model = Transaction
        fields = [
            'id',
            'wallet',
            'amount',
            'scheduled_time',
            'executed_time',
            'method',
            'status',
            'status_description',
        ]
        read_only_fields = ('executed_time', 'status_description')

    def validate_scheduled_time(self, value):
        """
        Validates the `scheduled_time` field to ensure it is in the future.

        Raises a `ValidationError` if the `scheduled_time` is in the past.
        If the transaction `method` is a withdrawal and no `scheduled_time`
        is provided, a default value of one minute in the future is used.
        """
        if value and value < timezone.now().timestamp():
            raise serializers.ValidationError("scheduled_time must be larger than now")
        if request := self.context.get('request'):
            method = request.data.get('method')
            if method == "1" and value is None:
                default = timezone.now() + timedelta(minutes=1)
                return default.timestamp()
        return value

    def save(self, **kwargs):
        """
        Saves the transaction object and schedules a job for a future withdrawal.

        If the `method` field is "0" (deposit), the `execute_deposit` method of the
        transaction instance is called.
        If the `method` field is "1" (withdrawal), a job is scheduled to call the
        `execute_withdraw` method of the transaction instance in the future.
        """
        super().save()
        method = self.validated_data.get('method')
        if method == "0":
            self.instance.execute_deposit()
        else:
            job = self.instance.execute_withdraw
            _id = str(self.instance.id)
            schedule = self.instance.scheduled_time
            schedule = datetime.fromtimestamp(schedule)
            define_schedule_job(job, schedule, (_id))
