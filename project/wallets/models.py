import uuid
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from utils import request_third_party_deposit


class Wallet(models.Model):
    """
    A class representing a user's wallet.

    Attributes:
    -----------
    uuid: uuid.UUID
        A unique identifier for the wallet.
    balance: decimal.Decimal
        The current balance of the wallet.
    owner: django.contrib.auth.models.User
        The user who owns the wallet.
    created_at: datetime.datetime
        The datetime when the wallet was created.
    updated_at: datetime.datetime
        The datetime when the wallet was last updated.
    """
    uuid = models.UUIDField(primary_key=True,
                            editable=False,
                            default=uuid.uuid4)
    balance = models.DecimalField(max_digits=12,
                                  decimal_places=2,
                                  default=Decimal("0.00"))
    owner = models.OneToOneField(User,
                                 on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def deposit(self, amount) -> [str, bool]:
        """
        Deposits the given amount into the wallet balance.
        Returns a tuple containing a message and a boolean indicating the success of the deposit.
        """
        self.balance += Decimal(amount)
        self.save()
        return "deposited successfully", True

    def withdraw(self, amount, request_third_party_deposit) -> [str, bool]:
        """
        Withdraws the given amount from the wallet balance.
        Returns a tuple containing a message and a boolean indicating the success of the withdrawal.
        If the withdrawal is successful, a request to a third party is made to process the transaction.
        """
        if self.balance < Decimal(amount):
            result_description = "Insufficient funds."
            result_status = False
        else:
            request_res: dict = request_third_party_deposit()
            result_status: bool = request_res.get('status') == 200
            result_description: str = request_res.get('data')
            if result_status:
                self.balance -= Decimal(amount)
            self.save()
        return result_description, result_status

    def __str__(self):
        """
        Returns a string representation of the owner's username.
        """
        return self.owner.username


class Transaction(models.Model):
    """
    A model to represent a financial transaction for a wallet.

    Attributes:
        wallet (Wallet): The foreign key to the Wallet model.
        amount (Decimal): The amount of the transaction.
        scheduled_time (int): The scheduled time for the transaction in timestamp format.
        executed_time (int): The execution time of the transaction in timestamp format.
        method (str): The method of the transaction, either deposit or withdraw.
        status (str): The status of the transaction, either pending, completed, or failed.
        status_description (str): A description of the status of the transaction.

    """
    class Status(models.TextChoices):
        PENDING = "0", _("PENDING")
        COMPLETED = "1", _("COMPLETED")
        FAILED = "2", _("FAILED")

    class Method(models.TextChoices):
        DEPOSIT = "0", _("DEPOSIT")
        WITHDRAW = "1", _("WITHDRAW")

    wallet = models.ForeignKey(Wallet,
                               on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12,
                                 decimal_places=2,
                                 default=Decimal("0.00"))
    scheduled_time = models.PositiveIntegerField(null=True)
    executed_time = models.PositiveIntegerField(null=True)
    method = models.CharField(max_length=1,
                              choices=Method.choices,
                              null=False, )
    status = models.CharField(max_length=1,
                              choices=Status.choices,
                              default=Status.PENDING, )
    status_description = models.TextField(null=True)

    def execute_deposit(self):
        """
        Executes a deposit transaction.
        """
        self.executed_time = timezone.now().timestamp()
        message, is_done = self.wallet.deposit(self.amount)
        self.status = self.Status.COMPLETED if is_done else self.Status.FAILED
        self.status_description = message
        self.save()

    def execute_withdraw(self):
        """
        Executes a withdraw transaction.
        """
        if self.executed_time is not None:
            message = "Transaction has already been executed."
            raise ValueError(message)
        if self.scheduled_time > timezone.now().timestamp():
            message = "Withdrawal time has not yet arrived."
            raise ValueError(message)
        message, is_done = self.wallet.withdraw(self.amount,
                                                request_third_party_deposit)
        self.status = self.Status.COMPLETED if is_done else self.Status.FAILED
        self.status_description = message
        self.executed_time = timezone.now().timestamp()
        self.save()

    def __str__(self) -> str:
        username = self.wallet.owner.username
        amount = self.amount
        status = self.status
        return f"username {username}, amount {amount}, status {status}"
