from datetime import timedelta, datetime

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers

from .models import Wallet, Transaction
from .scheduler import define_schedule_job


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class WalletSerializer(serializers.HyperlinkedModelSerializer):
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
        if value and value < timezone.now().timestamp():
            raise serializers.ValidationError("scheduled_time must be larger than now")
        if request := self.context.get('request'):
            method = request.data.get('method')
            if method == "1" and value is None:
                default = timezone.now() + timedelta(minutes=1)
                return default.timestamp()
        return value

    def save(self, **kwargs):
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
